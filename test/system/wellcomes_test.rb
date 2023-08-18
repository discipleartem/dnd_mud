require "application_system_test_case"

class WellcomesTest < ApplicationSystemTestCase
  setup do
    @wellcome = wellcomes(:one)
  end

  test "visiting the index" do
    visit wellcomes_url
    assert_selector "h1", text: "Wellcomes"
  end

  test "creating a Wellcome" do
    visit wellcomes_url
    click_on "New Wellcome"

    click_on "Create Wellcome"

    assert_text "Wellcome was successfully created"
    click_on "Back"
  end

  test "updating a Wellcome" do
    visit wellcomes_url
    click_on "Edit", match: :first

    click_on "Update Wellcome"

    assert_text "Wellcome was successfully updated"
    click_on "Back"
  end

  test "destroying a Wellcome" do
    visit wellcomes_url
    page.accept_confirm do
      click_on "Destroy", match: :first
    end

    assert_text "Wellcome was successfully destroyed"
  end
end
