import unittest
from unittest.mock import patch

import fetch_games as games


class GameScheduleTests(unittest.TestCase):
    def test_old_and_new_css_names_keep_date_and_platform(self):
        for card, title, platform in [
            ('ScheduleCard_scheduleCard__abc', 'ScheduleCard_gameTitleName__abc', 'gamePlatformTag__abc'),
            ('ScheduleCard-module-scss-module__abc__scheduleCard',
             'ScheduleCard-module-scss-module__abc__gameTitleName',
             'ScheduleListItem-module-scss-module__abc__gamePlatformTag'),
        ]:
            with self.subTest(card=card):
                page = f'''<h2>2026年10月29日（木）発売</h2>
                <a class="{card}" href="/game/title/123/page/1">
                <span class="{platform}">PS5</span>
                <b class="{title}">A &amp; B</b><p>1000円</p></a>
                <h2>2026年10月30日（金）発売</h2>
                <a class="{card}" href="/game/title/456/page/1">
                <b class="{title}">C</b></a>'''
                rows = games.parse(page)
                self.assertEqual([r['release_date'] for r in rows], ['2026-10-29', '2026-10-30'])
                self.assertEqual(rows[0]['title'], 'A & B')
                self.assertEqual(rows[0]['platforms'], ['PS5'])
                self.assertEqual(rows[1]['platforms'], [])

    def test_empty_response_never_overwrites_saved_data(self):
        with patch.object(games, 'fetch_html', return_value='<html>changed</html>'), \
             patch.object(games.C, 'publish') as publish:
            with self.assertRaises(RuntimeError):
                games.main()
            publish.assert_not_called()

    def test_partial_fetch_failure_never_publishes_incomplete_months(self):
        row = {'id': 'one', 'release_date': games.C.TODAY.isoformat()}
        with patch.object(games, 'months_around', return_value=['one', 'two']), \
             patch.object(games, 'fetch_html', side_effect=['ok', OSError('offline')]), \
             patch.object(games, 'parse', return_value=[row]), \
             patch.object(games.C, 'publish') as publish:
            with self.assertRaises(RuntimeError):
                games.main()
            publish.assert_not_called()


if __name__ == '__main__':
    unittest.main()
