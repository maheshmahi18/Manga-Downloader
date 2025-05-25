import unittest
import app
import json
import os
import shutil
from unittest.mock import patch

class TestApp(unittest.TestCase):
    def setUp(self):
        self.save_directory = "test_manga_downloads"
        app.SAVE_DIRECTORY = self.save_directory  # Override the SAVE_DIRECTORY in app.py
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    def tearDown(self):
        if os.path.exists(self.save_directory):
            shutil.rmtree(self.save_directory)

    @patch('app.process_episode')
    def test_download_manga_all_episodes_downloaded(self, mock_process_episode):
        # Scenario 1: All episodes downloaded
        start_chapter = 1
        end_chapter = 3
        total_episodes = end_chapter - start_chapter + 1

        # Configure mock to return a dummy PDF path for each episode
        mock_process_episode.side_effect = lambda base_url, ep_num, save_dir: os.path.join(save_dir, f"Episode_{ep_num}.pdf")

        response = self.client.post('/download_manga', json={
            'base_url': 'http://test.com',
            'start_chapter': str(start_chapter),
            'end_chapter': str(end_chapter)
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['all_episodes_downloaded'])
        self.assertEqual(len(data['files']), total_episodes)
        for i, file_info in enumerate(data['files']):
            self.assertEqual(file_info['episode'], f'Episode {start_chapter + i}')
            self.assertTrue(file_info['url'].endswith(f'Episode_{start_chapter + i}.pdf'))

    @patch('app.process_episode')
    def test_download_manga_some_episodes_fail(self, mock_process_episode):
        # Scenario 2: Some episodes fail
        start_chapter = 1
        end_chapter = 3
        
        # Configure mock: first succeeds, second fails, third succeeds
        def side_effect_logic(base_url, ep_num, save_dir):
            if ep_num == 1:
                return os.path.join(save_dir, f"Episode_{ep_num}.pdf")
            elif ep_num == 2:
                return None
            elif ep_num == 3:
                return os.path.join(save_dir, f"Episode_{ep_num}.pdf")
            return None
        mock_process_episode.side_effect = side_effect_logic

        response = self.client.post('/download_manga', json={
            'base_url': 'http://test.com',
            'start_chapter': str(start_chapter),
            'end_chapter': str(end_chapter)
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['all_episodes_downloaded'])
        self.assertEqual(len(data['files']), 2) # Only 2 should succeed
        self.assertEqual(data['files'][0]['episode'], 'Episode 1')
        self.assertEqual(data['files'][1]['episode'], 'Episode 3')


    @patch('app.process_episode')
    def test_download_manga_all_episodes_fail(self, mock_process_episode):
        # Scenario 3: No episodes downloaded (all fail)
        start_chapter = 1
        end_chapter = 3
        
        # Configure mock to always return None
        mock_process_episode.return_value = None

        response = self.client.post('/download_manga', json={
            'base_url': 'http://test.com',
            'start_chapter': str(start_chapter),
            'end_chapter': str(end_chapter)
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['all_episodes_downloaded'])
        self.assertEqual(len(data['files']), 0)

if __name__ == '__main__':
    unittest.main()
