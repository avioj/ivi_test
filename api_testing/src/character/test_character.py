from unittest import TestCase
import pytest
from requests.exceptions import HTTPError

from constants.character_service.LIMITS import COLLECTION_LIMIT
from constants.character_service.resp_text import LIMIT_PATTERN, NO_SUCH_NAME, IS_ALREADY_EXISTS
from ivi_backend_api.ivi_backend_api.model.factory import get_random_char
from ivi_backend_api.ivi_backend_api.errors.character_errors import CharNotFoundException

tc = TestCase()


class TestFunctional:

    def check_char(self, backend, char):
        tc.assertEqual(self.find_person(
            backend.characters.get_all_chars(), char["name"]),
            char)
        result = backend.characters.get_char(char["name"])
        tc.assertEqual(len(result), 1)
        tc.assertEqual(result[0], char)

    def find_person(self, characters, name):
        for char in characters:
            if char["name"] == name:
                return char
        raise CharNotFoundException()

    def person_creation_test(self, backend):
        char = get_random_char()
        response = backend.characters.create_char(char)
        tc.assertEqual(response, char)

        self.check_char(backend, char)

    def name_has_duplicate_test(self, backend):
        char = get_random_char()
        backend.characters.create_char(char)

        result = backend.characters.create_char(char)
        tc.assertEqual(result, IS_ALREADY_EXISTS.format(char["name"]))

    def name_availible_after_reset_test(self, backend):
        char = get_random_char()
        backend.characters.create_char(char)

        backend.characters.reset_collection()

        backend.characters.create_char(char)

        self.find_person(backend.characters.get_all_chars(), char["name"])
        backend.characters.get_char(char["name"])

    def char_update_test(self, backend):
        char = get_random_char()
        updated = get_random_char()
        updated.update(name=char["name"])
        backend.characters.create_char(char)
        backend.characters.update_char(char["name"], updated)
        self.check_char(backend, updated)

    def name_update_test(self, backend, randomizer):
        char = get_random_char()
        name_before = char["name"]
        backend.characters.create_char(char)
        char.update(name=randomizer.name())
        backend.characters.update_char(name_before, char)  # TODO: ask for spec
        self.check_char(backend, char)

    def update_name_to_null_test(self, backend):
        char = get_random_char()
        name_before = char["name"]
        backend.characters.create_char(char)
        with pytest.raises(HTTPError) as exc_info:
            backend.characters.update_char(name_before, {"name": None})
        tc.assertEqual(exc_info.response.status_code, 400)

    def update_name_to_exists_test(self, backend):
        first = get_random_char()
        second = get_random_char()
        second_name = second["name"]
        backend.characters.create_char(first)
        backend.characters.create_char(second)
        second.update(name=first["name"])
        with pytest.raises(HTTPError) as exc_info:
            backend.characters.update_char(second_name, second)
        tc.assertEqual(exc_info.response.status_code, 400)

    def updated_char_deletion_test(self, backend):
        char = get_random_char()
        updated = get_random_char()
        updated.update(name=char["name"])
        backend.characters.create_char(char)
        backend.characters.update_char(char["name"], updated)
        backend.characters.delete_char(char["name"])
        with pytest.raises(CharNotFoundException):
            self.find_person(backend.characters.get_all_chars(), char["name"])
        tc.assertEqual(backend.characters.get_char(char["name"]), NO_SUCH_NAME)

    def char_deletion_test(self, backend):
        char = get_random_char()
        backend.characters.create_char(char)
        backend.characters.delete_char(char["name"])
        with pytest.raises(CharNotFoundException):
            self.find_person(backend.characters.get_all_chars(), char["name"])
        tc.assertEqual(backend.characters.get_char(char["name"]), NO_SUCH_NAME)

    def char_deletion_negativ_test(self, backend):
        response = backend.characters.delete_char(get_random_char())[0]  # TODO: maybe add 404 status code to check
        backend.characters.assertEqual(response, NO_SUCH_NAME)

    def collection_reset_test(self, backend):
        before = len(backend.characters.get_all_chars())
        chars = [get_random_char() for _ in range(10)]
        for ch in chars:
            backend.characters.create_char(ch)
        backend.characters.reset_collection()
        after = backend.characters.get_all_chars()
        tc.assertEqual(before, len(after))
        names = [ch["name"] for ch in after]

        for ch in chars:
            tc.assertNotIn(ch["name"], names)

    def get_unreal_person_test(self, backend):
        result = backend.characters.get_char(get_random_char())
        tc.assertEqual(result, NO_SUCH_NAME)

    def check_limit_test(self, backend):
        before = len(backend.characters.get_all_chars())
        for _ in range(COLLECTION_LIMIT - before):
            backend.characters.create_char(get_random_char())
        with pytest.raises(HTTPError) as exc_info:
            backend.characters.create_char(get_random_char())
        tc.assertEqual(exc_info.response.status_code, 400)
        tc.assertEqual(exc_info.response.json()["error"], LIMIT_PATTERN.format(COLLECTION_LIMIT))
