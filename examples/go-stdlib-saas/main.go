// Syntyr SaaS example: a working, read-only, server-rendered interface.
// Standard library only; synthetic data; not an authentication or billing product.
package main

import (
	"bytes"
	"embed"
	"encoding/csv"
	"errors"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
	"unicode"
	"unicode/utf8"
)

//go:embed templates/*.html assets/syntyr.core.css
var files embed.FS

type customer struct {
	ID, Name, Plan, Status, Email, Href string
	MonthlyDollars                      int
}

var customers = []customer{
	{"cust-alpha", "Example Alpha Agency", "Starter", "active", "alpha@example.invalid", "", 249},
	{"cust-beacon", "Example Beacon Ops", "Growth", "active", "beacon@example.invalid", "", 999},
	{"cust-lumen", "Example Lumen Studio", "Trial", "trial", "lumen@example.invalid", "", 0},
	{"cust-vector", "Example Vector Commerce", "Growth", "past_due", "vector@example.invalid", "", 299},
	{"cust-orbit", "Example Orbit Tools", "Starter", "active", "orbit@example.invalid", "", 149},
	{"cust-delta", "Example Delta Labs", "Canceled", "canceled", "delta@example.invalid", "", 0},
}

type themeLink struct {
	Label, Href string
	Active      bool
}

type pageData struct {
	Page, Title, Theme, Q, Status, BackURL, ExportURL string
	OverviewURL, CustomersURL                         string
	Themes                                            []themeLink
	Customers                                         []customer
	Customer                                          customer
	ResultCount                                       int
	Total, Active, Trials                             int
	MRR                                               string
}

type app struct{ pages map[string]*template.Template }

func newApp() http.Handler {
	pages := make(map[string]*template.Template)
	for _, name := range []string{"overview", "customers", "detail"} {
		pages[name] = template.Must(template.ParseFS(files, "templates/base.html", "templates/"+name+".html"))
	}
	a := &app{pages: pages}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /{$}", a.overview)
	mux.HandleFunc("GET /customers", a.listCustomers)
	mux.HandleFunc("GET /customers/{id}", a.customerDetail)
	mux.HandleFunc("GET /customers.csv", a.exportCSV)
	mux.HandleFunc("GET /assets/syntyr.core.css", a.stylesheet)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Security-Policy", "default-src 'none'; script-src 'none'; style-src 'self'; img-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "no-referrer")
		mux.ServeHTTP(w, r)
	})
}

func themeFrom(r *http.Request) string {
	switch r.URL.Query().Get("theme") {
	case "studio", "grid", "noir":
		return r.URL.Query().Get("theme")
	default:
		return "studio"
	}
}

func buildURL(path string, v url.Values) string {
	if len(v) == 0 {
		return path
	}
	return path + "?" + v.Encode()
}

func navURL(path, theme string) string {
	return buildURL(path, url.Values{"theme": {theme}})
}

func (a *app) data(r *http.Request, page, title string) pageData {
	theme := themeFrom(r)
	d := pageData{Page: page, Title: title, Theme: theme, OverviewURL: navURL("/", theme), CustomersURL: navURL("/customers", theme)}
	for _, candidate := range []string{"studio", "grid", "noir"} {
		values := r.URL.Query()
		values.Set("theme", candidate)
		d.Themes = append(d.Themes, themeLink{
			Label:  strings.ToUpper(candidate[:1]) + candidate[1:],
			Href:   buildURL(r.URL.Path, values),
			Active: theme == candidate,
		})
	}
	return d
}

func (a *app) render(w http.ResponseWriter, name string, d pageData) {
	var b bytes.Buffer
	if err := a.pages[name].ExecuteTemplate(&b, "base", d); err != nil {
		log.Printf("render %s: %v", name, err)
		http.Error(w, "Internal template error", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	_, _ = b.WriteTo(w)
}

func (a *app) overview(w http.ResponseWriter, r *http.Request) {
	d := a.data(r, "overview", "Overview")
	d.Total = len(customers)
	mrr := 0
	for _, c := range customers {
		switch c.Status {
		case "active":
			d.Active++
			mrr += c.MonthlyDollars
		case "trial":
			d.Trials++
		}
	}
	d.MRR = dollars(mrr)
	a.render(w, "overview", d)
}

func dollars(v int) string {
	number := strconv.Itoa(v)
	for i := len(number) - 3; i > 0; i -= 3 {
		number = number[:i] + "," + number[i:]
	}
	return "$" + number
}

func parseFilters(r *http.Request) (query, status string, err error) {
	query = strings.TrimSpace(r.URL.Query().Get("q"))
	if utf8.RuneCountInString(query) > 100 {
		return "", "", errors.New("search query must be 100 characters or fewer")
	}
	status = r.URL.Query().Get("status")
	switch status {
	case "", "all", "active", "trial", "past_due", "canceled":
		if status == "" {
			status = "all"
		}
		return query, status, nil
	default:
		return "", "", errors.New("invalid status filter")
	}
}

func filtered(query, status string) []customer {
	var result []customer
	for _, c := range customers {
		if status != "all" && c.Status != status {
			continue
		}
		if !strings.Contains(strings.ToLower(c.Name+" "+c.Plan+" "+c.ID), strings.ToLower(query)) {
			continue
		}
		result = append(result, c)
	}
	return result
}

func (a *app) listCustomers(w http.ResponseWriter, r *http.Request) {
	q, status, err := parseFilters(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	d := a.data(r, "customers", "Customers")
	d.Q = q
	d.Status = status
	d.Customers = filtered(q, status)
	d.ResultCount = len(d.Customers)
	for i := range d.Customers {
		d.Customers[i].Href = navURL("/customers/"+d.Customers[i].ID, d.Theme)
	}
	values := url.Values{"theme": {d.Theme}, "status": {status}}
	if q != "" {
		values.Set("q", q)
	}
	d.ExportURL = buildURL("/customers.csv", values)
	a.render(w, "customers", d)
}

func (a *app) customerDetail(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	for _, c := range customers {
		if c.ID == id {
			d := a.data(r, "customers", "Customer detail")
			d.Customer = c
			d.BackURL = d.CustomersURL
			a.render(w, "detail", d)
			return
		}
	}
	http.NotFound(w, r)
}

func safeCSVCell(input string) string {
	trimmed := strings.TrimLeftFunc(input, unicode.IsSpace)
	if len(trimmed) > 0 && strings.ContainsRune("=+-@", rune(trimmed[0])) {
		return "'" + input
	}
	return input
}

func (a *app) exportCSV(w http.ResponseWriter, r *http.Request) {
	q, status, err := parseFilters(r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	var b bytes.Buffer
	writer := csv.NewWriter(&b)
	_ = writer.Write([]string{"id", "name", "status", "monthly_usd"})
	for _, c := range filtered(q, status) {
		_ = writer.Write([]string{safeCSVCell(c.ID), safeCSVCell(c.Name), safeCSVCell(c.Status), strconv.Itoa(c.MonthlyDollars)})
	}
	writer.Flush()
	if err := writer.Error(); err != nil {
		http.Error(w, "CSV generation failed", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/csv; charset=utf-8")
	w.Header().Set("Content-Disposition", `attachment; filename="syntyr-example-customers.csv"`)
	w.Header().Set("Cache-Control", "no-store")
	_, _ = w.Write(b.Bytes())
}

func (a *app) stylesheet(w http.ResponseWriter, r *http.Request) {
	css, err := files.ReadFile("assets/syntyr.core.css")
	if err != nil {
		http.Error(w, "Stylesheet unavailable", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/css; charset=utf-8")
	w.Header().Set("Cache-Control", "public, max-age=3600")
	_, _ = w.Write(css)
}

func main() {
	server := &http.Server{Addr: "127.0.0.1:8080", Handler: newApp(), ReadHeaderTimeout: 5 * time.Second}
	fmt.Fprintln(os.Stdout, "Syntyr example: http://127.0.0.1:8080 (synthetic read-only data)")
	log.Fatal(server.ListenAndServe())
}
