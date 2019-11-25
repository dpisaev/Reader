"""
Модуль с тестами для VK бота.
"""

import unittest
import in_social.Vk_Bot
import json


class TestVkBot(unittest.TestCase):
    def setUp(self):
        """
        Метод подготовки данных для тестов
        """
        self.vk = in_social.Vk_Bot.VKBot()

    def test_build_vk_bot(self):
        self.assertIsNone(self.vk.keyboard)
        self.assertIsNone(self.vk.event)
        self.assertIsNone(self.vk.state)
        self.assertIsNone(self.vk.post)
        self.assertIsNone(self.vk.tag)

    def test_get_color(self):
        self.assertEqual(self.vk.get_color(0), 'positive')
        self.assertEqual(self.vk.get_color(1), 'negative')
        self.assertEqual(self.vk.get_color(2), 'primary')

    def test_checked_on_false_messanges_False(self):
        messanges = '/start'
        context = ['hello', 'buy']
        self.assertFalse(self.vk.checked_on_false_messenge(messanges, *context))

    def test_checked_on_false_messanges_True(self):
        messanges = '/start'
        context = ['hello', 'buy', '/start']
        self.assertTrue(self.vk.checked_on_false_messenge(messanges, *context))

    def test_change_stage(self):
        self.assertIsNone(self.vk.change_state(new_state='checked'))

    def test_get_button(self):
        button = {
            'action': {
                'type': "text",
                'payload': json.dumps(''),
                'label': 'test'
            },
            'color': 'primary'
        }
        self.assertEqual(self.vk.get_button(label='test', color='primary'), button)



