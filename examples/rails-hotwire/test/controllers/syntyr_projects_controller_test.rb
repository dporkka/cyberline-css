require "test_helper"

class SyntyrProjectsControllerTest < ActionDispatch::IntegrationTest
  test "GET search keeps accessible results and filters rows" do
    get syntyr_projects_url, params: { q: "airport" }
    assert_response :success
    assert_select "turbo-frame#syntyr-project-results", 1
    assert_select "table tbody tr", 1
    assert_select "td", text: "Airport displays"
    assert_select "input#syntyr-project-query[value='airport']", 1
  end

  test "GET search escapes user input and renders an empty result" do
    get syntyr_projects_url, params: { q: "<script>alert(1)</script>" }
    assert_response :success
    assert_select "table tbody tr", 0
    assert_select "p", text: /No matching projects/
    assert_select "script", 0
  end
end
