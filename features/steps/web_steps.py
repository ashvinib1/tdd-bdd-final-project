# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = 30
ID_PREFIX = 'product_'


@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title


@then('I should not see "{message}"')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message not in context.driver.page_source


@when(u'I set the "{field_name}" to "{value}"')
def step_impl(context, field_name, value):
    """ Set the value of an input field """
    element_id = ID_PREFIX + field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(value)


@when(u'I select "{value}" in the "{dropdown_name}" dropdown')
def step_impl(context, value, dropdown_name):
    """ Select a value from a dropdown """
    element_id = ID_PREFIX + dropdown_name.lower().replace(' ', '_')
    select = Select(context.driver.find_element(By.ID, element_id))
    select.select_by_visible_text(value)


@when(u'I press the "{button}" button')
@then(u'I press the "{button}" button')
def step_impl(context, button):
    """ Press the button """
    button_id = button.lower().replace(' ', '_') + '-btn'
    context.driver.find_element(By.ID, button_id).click()


@then(u'I should see "{value}" in the "{field_name}" field')
def step_impl(context, value, field_name):
    """ Check the value of an input field """
    element_id = ID_PREFIX + field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute('value') == value


@then(u'I should see "{value}" in the "{dropdown_name}" dropdown')
def step_impl(context, value, dropdown_name):
    """ Check the selected value of a dropdown """
    element_id = ID_PREFIX + dropdown_name.lower().replace(' ', '_')
    select = Select(context.driver.find_element(By.ID, element_id))
    assert select.first_selected_option.text == value


@then('the "{field_name}" field should be empty')
def step_impl(context, field_name):
    """ Check if an input field is empty """
    element_id = ID_PREFIX + field_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute('value') == ''


@then(u'I should see the message "{message}"')
def step_impl(context, message):
    """ Check the flash message """
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert found


@then(u'I should see "{name}" in the results')
def step_impl(context, name):
    """ Check if the name is in the search results """
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    assert found


@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    """ Check if the name is not in the search results """
    element = context.driver.find_element(By.ID, 'search_results')
    assert name not in element.text


@then(u'I should see "{count}" rows')
def step_impl(context, count):
    """ Check the number of rows in the results table with explicit wait """
    expected_count = int(count)

    # Wait until at least one row appears or table body is present
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#search_results tbody tr")
        )
    )

    # Fetch all rows after the wait
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results tbody tr")
    logging.info("Found %d rows, expected %d", len(rows), expected_count)

    assert len(rows) == expected_count, f"Expected {expected_count} rows but found {len(rows)}"


@when(u'I copy the "{field_name}" field')
def step_impl(context, field_name):
    """ Copy text from an input field """
    element_id = ID_PREFIX + field_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Copied "%s" from "%s"', context.clipboard, field_name)
    assert context.clipboard is not None


@when(u'I paste the "{field_name}" field')
@then(u'I paste the "{field_name}" field')
def step_impl(context, field_name):
    """ Paste text into an input field """
    element_id = ID_PREFIX + field_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)
    logging.info('Pasted "%s" into "%s"', context.clipboard, field_name)
