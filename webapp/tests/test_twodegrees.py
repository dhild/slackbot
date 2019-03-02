from app.twodegrees import *
import unittest


class PersonFinderTestCase(unittest.TestCase):

    def test_one_person(self):
        recognizer = PersonFinder()
        person = recognizer('Do you know Neal Stephenson?')
        self.assertEqual(person, 'Neal Stephenson')

    def test_no_people_in_pr_message(self):
        recognizer = PersonFinder()
        person = recognizer(':pull-request: https://some/url - I made changes to stuff')
        self.assertIsNone(person)

    def test_no_people_in_conversation(self):
        recognizer = PersonFinder()
        for text in [
            'Time for standup!',
            'Has anyone tried out go 1.12?',
            'In case anyone need this: ',
            'Anyone going or want to go to Seapine at 4:30p today?',
            "Don't forget to vote on your Tenets! Voting closes tomorrow at noon:",
            "hi team, the demo video is available in Bluejeans here https://bluejeans.com/s/xxxxx Can you please tell "
            "me if you have access to it? Where can/should I store it  (413MB) so that everybody has access to it? it "
            "is too big for confluence , or at least it goes in error with me … ",
            "Missing standup\nYesterday: Identified missing Prometheus configuration when deploying fluentd component "
            "in alpha us east .Prometheus configuration settings existed in alpha USW2 already but those were not "
            "codified in component. Created a PR after making final changes to component\nToday: Will be working on "
            "deploying these changes in non prod environments\nNo blockers "
        ]:
            person = recognizer(text)
            self.assertIsNone(person)


class CasualReferencerTestCase(unittest.TestCase):

    def test_casual_reference(self):
        referencer = CasualReferencer()
        ref = referencer('Hugh Jackman')
        self.assertIn('Hugh Jackman', ref)


if __name__ == '__main__':
    unittest.main()
