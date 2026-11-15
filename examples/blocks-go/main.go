// A minimal server-rendered Syntyr consumer, with Go standard library only.
// Run the Syntyr block installer from the repository before starting this app.
package main

import (
	"embed"
	"errors"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

//go:embed templates/dashboard.html
var templates embed.FS

type dashboardData struct {
	Account        string
	ActiveAccounts string
	OpenRequests   string
	Completion     string
}

func newHandler(publicRoot string) (http.Handler, error) {
	cssDir := filepath.Join(publicRoot, "syntyr", "css")
	cssFile := filepath.Join(cssDir, "syntyr.core.css")
	info, err := os.Stat(cssFile)
	if err != nil {
		return nil, errors.New("missing installed Syntyr core CSS; run python3 ../../scripts/blocks_cli.py install metric-overview --output .")
	}
	if !info.Mode().IsRegular() {
		return nil, errors.New("installed Syntyr CSS is not a regular file")
	}
	page, err := template.ParseFS(templates, "templates/dashboard.html")
	if err != nil {
		return nil, err
	}

	mux := http.NewServeMux()
	mux.Handle("GET /syntyr/css/", http.StripPrefix("/syntyr/css/", http.FileServer(http.Dir(cssDir))))
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		account := strings.TrimSpace(r.URL.Query().Get("account"))
		if account == "" {
			account = "Demo workspace"
		}
		// Illustrative metrics. Replace these with authorized application data.
		data := dashboardData{
			Account:        account,
			ActiveAccounts: "1,284",
			OpenRequests:   "38",
			Completion:     "94%",
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		if err := page.Execute(w, data); err != nil {
			log.Printf("render dashboard: %v", err)
		}
	})
	return mux, nil
}

func main() {
	handler, err := newHandler(".")
	if err != nil {
		log.Fatal(err)
	}
	server := &http.Server{
		Addr:              "127.0.0.1:8080",
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Printf("Syntyr Go sample: http://127.0.0.1:8080/")
	log.Fatal(server.ListenAndServe())
}
