package main

import (
	"encoding/csv"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
)

func request(path string) *httptest.ResponseRecorder {
	r := httptest.NewRecorder()
	newApp().ServeHTTP(r, httptest.NewRequest(http.MethodGet, path, nil))
	return r
}

func TestOverviewShowsServerCalculatedMetricsAndNativeUI(t *testing.T) {
	r := request("/")
	if r.Code != http.StatusOK {
		t.Fatalf("overview: %d: %s", r.Code, r.Body)
	}
	body := r.Body.String()
	for _, phrase := range []string{"$1,397", "Active subscriptions", "6 customers", "SYNTHETIC DATA", "data-syn-theme=\"studio\"", "href=\"/assets/syntyr.core.css\"", "Skip to main content"} {
		if !strings.Contains(body, phrase) {
			t.Errorf("overview missing %q", phrase)
		}
	}
	if strings.Contains(strings.ToLower(body), "<script") {
		t.Error("runtime JS unexpectedly present")
	}
	if got := r.Header().Get("Content-Security-Policy"); !strings.Contains(got, "script-src 'none'") {
		t.Errorf("CSP must disallow scripts: %q", got)
	}
}

func TestSearchAndFilterRunOnServer(t *testing.T) {
	r := request("/customers?status=active&q=alpha")
	if r.Code != http.StatusOK {
		t.Fatalf("customers: %d: %s", r.Code, r.Body)
	}
	body := r.Body.String()
	if !strings.Contains(body, "Example Alpha Agency") {
		t.Error("matching customer missing")
	}
	if strings.Contains(body, "Example Beacon Ops") || strings.Contains(body, "Example Lumen Studio") {
		t.Error("server failed to filter nonmatching rows")
	}
	if !strings.Contains(body, "1 matching customer") {
		t.Error("missing result count")
	}
	if !strings.Contains(body, "name=\"q\"") || !strings.Contains(body, "method=\"get\"") {
		t.Error("no working native GET search")
	}
	if !strings.Contains(body, "/customers.csv?") {
		t.Error("filtered CSV export link missing")
	}
}

func TestEscapingAndInvalidFilters(t *testing.T) {
	query := url.QueryEscape(`"><svg onload=alert(1)>`)
	r := request("/customers?q=" + query)
	if r.Code != http.StatusOK {
		t.Fatalf("search returned %d", r.Code)
	}
	if strings.Contains(r.Body.String(), "<svg") {
		t.Error("unescaped user input reached HTML")
	}
	if !strings.Contains(r.Body.String(), "&lt;svg") {
		t.Error("search input not escaped back to input value")
	}
	for _, path := range []string{"/customers?status=oops", "/customers.csv?status=oops"} {
		if got := request(path).Code; got != http.StatusBadRequest {
			t.Errorf("%s: got %d, want 400", path, got)
		}
	}
}

func TestThemeAndSearchContextCarryBetweenPages(t *testing.T) {
	r := request("/customers?theme=noir&q=alpha&status=active")
	body := r.Body.String()
	if !strings.Contains(body, `data-syn-theme="noir"`) {
		t.Error("theme did not render")
	}
	if !strings.Contains(body, `href="/customers/cust-alpha?theme=noir"`) {
		t.Error("detail link lost theme")
	}
	if !strings.Contains(body, `href="/customers?q=alpha&amp;status=active&amp;theme=grid"`) {
		t.Error("theme change did not preserve current search and filter")
	}
	detail := request("/customers/cust-alpha?theme=noir")
	if detail.Code != http.StatusOK || !strings.Contains(detail.Body.String(), `data-syn-theme="noir"`) {
		t.Error("detail did not keep selected theme")
	}
	if !strings.Contains(detail.Body.String(), `href="/customers?theme=noir"`) {
		t.Error("detail back link lost theme")
	}
	fallback := request("/?theme=unknown")
	if !strings.Contains(fallback.Body.String(), `data-syn-theme="studio"`) {
		t.Error("invalid theme not safely defaulted")
	}
}

func TestDetailNotFoundAndNoMutations(t *testing.T) {
	if got := request("/customers/nonexistent").Code; got != http.StatusNotFound {
		t.Errorf("unknown detail: %d", got)
	}
	r := httptest.NewRecorder()
	newApp().ServeHTTP(r, httptest.NewRequest(http.MethodPost, "/customers", nil))
	if r.Code != http.StatusMethodNotAllowed {
		t.Errorf("POST must not mutate demo, got %d", r.Code)
	}
}

func TestCSVExportHonorsFiltersAndEscapesCells(t *testing.T) {
	r := request("/customers.csv?status=active&q=alpha")
	if r.Code != http.StatusOK {
		t.Fatalf("CSV: %d", r.Code)
	}
	if !strings.HasPrefix(r.Header().Get("Content-Type"), "text/csv") {
		t.Error("CSV content type missing")
	}
	if !strings.Contains(r.Header().Get("Content-Disposition"), "attachment") {
		t.Error("download header missing")
	}
	rows, err := csv.NewReader(strings.NewReader(r.Body.String())).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 2 || len(rows[0]) != 4 || rows[1][0] != "cust-alpha" || rows[1][1] != "Example Alpha Agency" {
		t.Errorf("incorrect filtered CSV: %v", rows)
	}
	for _, value := range []string{"=2+3", "+1+2", "-10", "@SUM(A1)", "\t=SUM(1,1)", "\r@cmd"} {
		if got := safeCSVCell(value); !strings.HasPrefix(got, "'") {
			t.Errorf("unsafe cell %q escaped as %q", value, got)
		}
	}
	if got := safeCSVCell("Ordinary Customer"); got != "Ordinary Customer" {
		t.Errorf("ordinary cell unexpectedly changed: %q", got)
	}
}

func TestStylesheetIsSelfHostedAndScriptFree(t *testing.T) {
	r := request("/assets/syntyr.core.css")
	if r.Code != http.StatusOK {
		t.Fatalf("CSS: %d", r.Code)
	}
	if !strings.HasPrefix(r.Header().Get("Content-Type"), "text/css") {
		t.Error("CSS served with wrong type")
	}
	if !strings.Contains(r.Body.String(), ".syn-root") {
		t.Error("vendored CSS seems missing")
	}
}
