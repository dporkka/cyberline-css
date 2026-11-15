# Demonstration-only data; replace with authorized Active Record scopes in your app.
class SyntyrProjectsController < ApplicationController
  PROJECTS = [
    { name: "Station expansion", owner: "Operations", status: "In progress" },
    { name: "Airport displays", owner: "Sales", status: "Review" },
    { name: "Downtown refresh", owner: "Production", status: "Planned" }
  ].freeze

  def index
    raw = params[:q]
    @query = raw.is_a?(String) ? raw.strip[0, 100] : ""
    @projects = PROJECTS.select do |project|
      project[:name].downcase.include?(@query.downcase)
    end
  end
end
