import requests
from faker import Faker
import random
from unittest import TestCase
import logging
import traceback
import argparse
from json.decoder import JSONDecodeError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('log_filename.txt')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class CharNotFoundException(Exception):
    pass


class Randomizer:
    faker = Faker()

    @staticmethod
    def get_name():
        return Randomizer.faker.word()

    @staticmethod
    def get_text():
        return " ".join(Randomizer.faker.words())

    @staticmethod
    def get_int():
        return random.randint(10, 200)

    @staticmethod
    def get_float():
        return random.uniform(10, 200)

    @staticmethod
    def get_random_char():
        return {"name": Randomizer.get_name(),
                "universe": Randomizer.get_text(),
                "education": Randomizer.get_text(),
                "weight": Randomizer.get_int(),
                "height": Randomizer.get_float(),
                "identity": Randomizer.get_text(),
                "other_aliases": "None"}


class TempApiSolution:
    default_headers = {
        'Content-type': 'application/json',
        'cache-control': 'no-cache,no-cache',
    }

    def __init__(self, host, login, password):
        self.host = host
        self.credentials = (login, password)
        self.session = requests.Session()

    def create_char(self, data):
        response = self._post('character', headers=self.default_headers,
                              json=data,
                              auth=self.credentials)
        return response["result"]

    def update_char(self, name, char_fields):
        response = self._put('character/{}'.format(name), headers=self.default_headers,
                             json=char_fields,
                             auth=self.credentials)
        return response["result"]

    def delete_char(self, char_name):
        response = self._delete('character/{}'.format(char_name), headers=self.default_headers,
                                auth=self.credentials)
        return response["result"]

    def reset_collection(self):
        return self._post('reset', headers=self.default_headers,
                          auth=self.credentials)

    def get_all_chars(self):
        response = self._get('characters', headers=self.default_headers,
                             auth=self.credentials)
        return response["result"]

    def get_char(self, name):
        response = self._get('character/{}'.format(name), headers=self.default_headers, auth=self.credentials)
        return response["result"]

    def _delete(self, url, **kwargs):
        callback = self.session.delete
        return self._send(url, callback, 'DELETE', **kwargs)

    def _put(self, url, **kwargs):
        callback = self.session.put
        return self._send(url, callback, 'PUT', **kwargs)

    def _get(self, url, **kwargs):
        callback = self.session.get
        return self._send(url, callback, 'GET', **kwargs)

    def _post(self, url, **kwargs):
        callback = self.session.post
        return self._send(url, callback, 'POST', **kwargs)

    def _send(self, url, callback, method, **kwargs):
        log_msg = 'Sending {} request to {}'.format(method, url)

        log_msg = '{} and headers {} and auth {}'.format(log_msg, kwargs.get('headers'), kwargs.get("auth"))
        json_data = kwargs.get("json")
        if json_data is not None:
            log_msg = "{} and body {}".format(log_msg, json_data)
        logger.debug(log_msg)
        response = callback(self.get_path(url), **kwargs)
        response.raise_for_status()
        logger.debug('Response: %s' % response.text)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text

    def get_path(self, url):
        return "{}/{}".format(self.host, url)


class FunctionalCases:
    LIMIT = 300

    def __init__(self, host, login, password):
        self.api = TempApiSolution(host, login, password)
        self.tc = TestCase()

    def check_char(self, char):
        self.tc.assertEqual(self.find_person(
            self.api.get_all_chars(), char["name"]),
            char)
        result = self.api.get_char(char["name"])
        self.tc.assertEqual(len(result), 1)
        self.tc.assertEqual(result[0], char)

    def find_person(self, characters, name):
        for char in characters:
            if char["name"] == name:
                return char
        raise CharNotFoundException()

    def person_creation_test(self):
        char = Randomizer.get_random_char()
        response = self.api.create_char(char)
        self.tc.assertEqual(response, char)

        self.check_char(char)

    def name_has_duplicate_test(self):
        char = Randomizer.get_random_char()
        self.api.create_char(char)

        result = self.api.create_char(char)
        self.tc.assertEqual(result, "{} is already exists".format(char["name"]))

    def name_availible_after_reset_test(self):
        char = Randomizer.get_random_char()
        self.api.create_char(char)

        self.api.reset_collection()

        self.api.create_char(char)

        self.find_person(self.api.get_all_chars(), char["name"])
        self.api.get_char(char["name"])

    def char_update_test(self):
        char = Randomizer.get_random_char()
        updated = Randomizer.get_random_char()
        updated.update(name=char["name"])
        self.api.create_char(char)
        self.api.update_char(char["name"], updated)
        self.check_char(updated)

    def name_update_test(self):
        char = Randomizer.get_random_char()
        name_before = char["name"]
        self.api.create_char(char)
        char.update(name=Randomizer.get_name())
        self.api.update_char(name_before, char)  # TODO: ask for spec
        self.check_char(char)

    def update_name_to_null_test(self):
        char = Randomizer.get_random_char()
        name_before = char["name"]
        self.api.create_char(char)
        try:
            self.api.update_char(name_before, {"name": None})
        except requests.HTTPError as err:
            self.tc.assertEqual(err.response.status_code, 400)

    def update_name_to_exists_test(self):
        first = Randomizer.get_random_char()
        second = Randomizer.get_random_char()
        second_name = second["name"]
        self.api.create_char(first)
        self.api.create_char(second)
        second.update(name=first["name"])
        try:
            self.api.update_char(second_name, second)
        except requests.HTTPError as err:
            self.tc.assertEqual(err.response.status_code, 400)

    def updated_char_deletion_test(self):
        char = Randomizer.get_random_char()
        updated = Randomizer.get_random_char()
        updated.update(name=char["name"])
        self.api.create_char(char)
        self.api.update_char(char["name"], updated)
        self.api.delete_char(char["name"])
        try:
            self.find_person(self.api.get_all_chars(), char["name"])
        except CharNotFoundException:
            pass
        else:
            self.tc.fail("expected not found for {} char".format(char["name"]))

        self.tc.assertEqual(self.api.get_char(char["name"]), 'No such name')

    def char_deletion_test(self):
        char = Randomizer.get_random_char()
        self.api.create_char(char)
        self.api.delete_char(char["name"])
        try:
            self.find_person(self.api.get_all_chars(), char["name"])
        except CharNotFoundException:
            pass
        else:
            self.tc.fail("expected 404")
        self.tc.assertEqual(self.api.get_char(char["name"]), 'No such name')

    def char_deletion_negativ_test(self):
        response = self.api.delete_char(Randomizer.get_name())[0]  # TODO: maybe add 404 status code to check
        self.tc.assertEqual(response, 'No such name')

    def collection_reset_test(self):
        before = len(self.api.get_all_chars())
        chars = [Randomizer.get_random_char() for _ in range(10)]
        for ch in chars:
            self.api.create_char(ch)
        self.api.reset_collection()
        after = self.api.get_all_chars()
        self.tc.assertEqual(before, len(after))
        names = [ch["name"] for ch in after]

        for ch in chars:
            self.tc.assertNotIn(ch["name"], names)

    def get_unreal_person_test(self):
        result = self.api.get_char(Randomizer.get_name())
        self.tc.assertEqual(result, 'No such name')

    def check_limit_test(self):
        before = len(self.api.get_all_chars())
        for _ in range(self.LIMIT - before):
            self.api.create_char(Randomizer.get_random_char())
        try:
            self.api.create_char(Randomizer.get_random_char())
        except requests.exceptions.HTTPError as err:
            self.tc.assertEqual(err.response.status_code, 400)
            self.tc.assertEqual(err.response.json()["error"], "Collection can't contain more than 500 items")
        else:
            self.tc.fail("limit error")

    def run(self):
        for name in dir(self):
            if "_test" in name:
                logger.debug("running case with name {}".format("name"))
                try:
                    method = getattr(self, name)
                    method()
                except Exception as err:
                    logger.error("case {} was failed , original error is  {}".format(name, err))
                    traceback.print_exc()
                logger.debug("case with name {} passed ! =)".format(name))
                self.api.reset_collection()


parser = argparse.ArgumentParser(description='Quick solution to simplify backend testing')

parser.add_argument('--url', type=str, dest='url')
parser.add_argument('--login', type=str, dest='login')
parser.add_argument('--password', type=str, dest='password')
args = parser.parse_args()
FunctionalCases(args.url, args.login, args.password).run()
