// Syntyr backend parity example. No external Go dependencies or JS.
package main

import (
	"embed"
	"html/template"
	"log"
	"net/http"
	"strings"
)

//go:embed templates/index.gohtml
var templates embed.FS

var page = template.Must(template.ParseFS(templates, "templates/index.gohtml"))

type project struct {
	Name   string
	Owner  string
	Status string
}

var projects = []project{
	{"Station expansion", "Operations", "In progress"},
	{"Airport displays", "Sales", "Review"},
	{"Downtown refresh", "Production", "Planned"},
}

type pageData struct {
	Query    string
	Projects []project
}

func projectsHandler(w http.ResponseWriter, r *http.Request) {
	query := strings.TrimSpace(r.URL.Query().Get("q"))
	if runes := []rune(query); len(runes) > 100 {
		query = string(runes[:100])
	}

	filtered := make([]project, 0, len(projects))
	for _, item := range projects {
		if strings.Contains(strings.ToLower(item.Name), strings.ToLower(query)) {
			filtered = append(filtered, item)
		}
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := page.ExecuteTemplate(w, "index.gohtml", pageData{Query: query, Projects: filtered}); err != nil {
		log.Printf("template rendering error: %v", err)
	}
}

func newHandler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /syntyr/projects", projectsHandler)
	mux.Handle("GET /css/", http.FileServer(http.Dir("public")))
	return mux
}

func main() {
	log.Println("Syntyr Go projects demo at http://127.0.0.1:8080/syntyr/projects")
	log.Fatal(http.ListenAndServe("127.0.0.1:8080", newHandler()))
}
