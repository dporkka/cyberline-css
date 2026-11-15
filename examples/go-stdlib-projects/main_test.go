package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestProjectsSearchMatchesAcrossBackends(t *testing.T) {
	for _, tc := range []struct {
		name         string
		query        string
		expectedRows int
		contains     string
	}{
		{"all", "", 3, "Station expansion"},
		{"filtered", " AIRPORT ", 1, "Airport displays"},
		{"empty", "not-found", 0, "No matching projects"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(http.MethodGet, "/syntyr/projects?q="+strings.ReplaceAll(tc.query, " ", "+"), nil)
			recorder := httptest.NewRecorder()
			newHandler().ServeHTTP(recorder, req)
			response := recorder.Body.String()
			if recorder.Code != http.StatusOK {
				t.Fatalf("HTTP %d: %s", recorder.Code, response)
			}
			if strings.Count(response, "<tr data-project-row>") != tc.expectedRows {
				t.Fatalf("wrong row count: %s", response)
			}
			if tc.expectedRows > 0 && (!strings.Contains(response, `class="syn-table"`) || !strings.Contains(response, `scope="col"`)) {
				t.Fatalf("missing accessible table: %s", response)
			}
			if !strings.Contains(response, tc.contains) {
				t.Fatalf("missing %q: %s", tc.contains, response)
			}
			for _, required := range []string{`class="syn-root`, `aria-live="polite"`, `method="get"`} {
				if !strings.Contains(response, required) {
					t.Fatalf("missing %s", required)
				}
			}
		})
	}
}

func TestProjectsSearchEscapesUserInput(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/syntyr/projects?q=%3Cscript%3Ealert%281%29%3C%2Fscript%3E", nil)
	recorder := httptest.NewRecorder()
	newHandler().ServeHTTP(recorder, req)
	body := recorder.Body.String()
	if strings.Contains(body, "<script>") {
		t.Fatalf("unsafe unescaped markup: %s", body)
	}
	if !strings.Contains(body, "&lt;script&gt;alert(1)&lt;/script&gt;") {
		t.Fatalf("missing escaped input: %s", body)
	}
}
