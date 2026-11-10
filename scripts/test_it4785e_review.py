"""Regression checks for reviewed IT4785E answer content and stale-key protection."""
import copy
import json
from pathlib import Path
import unittest

from it4785e_review import review_bank

ROOT = Path(__file__).resolve().parents[1]


def generated(name):
    content = (ROOT / 'dist/IT4785E' / name).read_text()
    return json.loads(content.split('window.CHAPTERS = ', 1)[1].rstrip().removesuffix(';'))


class AnswerReviewTests(unittest.TestCase):
    def setUp(self):
        self.bank = generated('data.js')
        self.questions = {q['id']: q for c in self.bank for q in c['questions']}

    def test_review_covers_every_question_and_midterm_uses_same_answers(self):
        self.assertEqual(len(self.questions), 260)
        google = {q['id']: q for c in generated('google.js') for q in c['questions']}
        self.assertEqual(len(google), 87)
        all_questions = self.questions | google
        for q in all_questions.values():
            self.assertGreater(len(q['explanation']), 100, q['id'])
            self.assertTrue(q['references'], q['id'])
            self.assertTrue(set(q['answers']) <= {o['id'] for o in q['options']}, q['id'])
        midterm = [q for c in generated('midterm.js') for q in c['questions']]
        self.assertEqual(len(midterm), 106)
        for q in midterm:
            original = all_questions[q['id']]
            for key in ('answers', 'explanation', 'references'):
                self.assertEqual(q[key], original[key], (q['id'], key))

    def test_image_scaling_and_abstract_class_corrections(self):
        self.assertEqual(self.questions['20241-4-3']['answers'], ['B'])
        self.assertEqual(self.questions['20231-1-26']['answers'], ['A', 'C'])
        self.assertEqual(self.questions['20231-2-20']['answers'], ['A'])
        self.assertEqual(self.questions['20231-3-4']['answers'], ['B', 'D'])

    def test_ambiguous_or_truncated_questions_are_not_forced(self):
        for question_id in ('20231-1-29', '20231-4-34', '20231-4-36', '20231-1-19', '20241-2-20'):
            self.assertEqual(self.questions[question_id]['answers'], [])
        ungraded = [q for q in self.questions.values() if not q['answers'] and not q.get('fields')]
        self.assertEqual(len(ungraded), 39)

    def test_all_google_keys_have_matching_submit_evidence(self):
        quizzes = json.loads((ROOT / 'scripts/google_quizzes.json').read_text())
        keys = json.loads((ROOT / 'scripts/google_quiz_answers.json').read_text())
        for quiz in quizzes:
            for q in quiz['questions']:
                key = keys[q['id']]
                self.assertEqual(key['fingerprint'], q['fingerprint'])
                self.assertGreater(key['verification']['total'], 0)
                self.assertEqual(key['verification']['score'], key['verification']['total'])

    def test_changed_question_stops_generation(self):
        chapters = []
        for path in sorted((ROOT.parent / 'IT4785E').glob('chap*.json')):
            questions = []
            for row in json.loads(path.read_text())['list']:
                raw = row['cau_hoi']
                q = dict(id=raw['id'], text=raw['noi_dung'], type=raw['loai'],
                         options=[{'id': o['id'], 'text': o['content']} for o in raw['lua_chon']],
                         answers=raw['dap_an'])
                if 'fields' in raw:
                    q['fields'] = raw['fields']
                questions.append(q)
            chapters.append({'questions': questions})
        review_bank(copy.deepcopy(chapters))
        chapters[0]['questions'][0]['options'][0]['text'] = 'Changed question option'
        with self.assertRaisesRegex(ValueError, 'nội dung đã thay đổi'):
            review_bank(chapters)


if __name__ == '__main__':
    unittest.main()
