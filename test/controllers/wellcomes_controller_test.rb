require 'test_helper'

class WellcomesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @wellcome = wellcomes(:one)
  end

  test "should get index" do
    get wellcomes_url
    assert_response :success
  end

  test "should get new" do
    get new_wellcome_url
    assert_response :success
  end

  test "should create wellcome" do
    assert_difference('Wellcome.count') do
      post wellcomes_url, params: { wellcome: {  } }
    end

    assert_redirected_to wellcome_url(Wellcome.last)
  end

  test "should show wellcome" do
    get wellcome_url(@wellcome)
    assert_response :success
  end

  test "should get edit" do
    get edit_wellcome_url(@wellcome)
    assert_response :success
  end

  test "should update wellcome" do
    patch wellcome_url(@wellcome), params: { wellcome: {  } }
    assert_redirected_to wellcome_url(@wellcome)
  end

  test "should destroy wellcome" do
    assert_difference('Wellcome.count', -1) do
      delete wellcome_url(@wellcome)
    end

    assert_redirected_to wellcomes_url
  end
end
