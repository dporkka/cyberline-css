package main

import (
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func installedFixture(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	cmd := exec.Command("python3", "../../scripts/blocks_cli.py", "install", "metric-overview", "--output", root)
	if output, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("Syntyr CLI failed: %v\n%s", err, output)
	}
	return root
}

func TestInstalledCoreStylesheetAndRenderedPage(t *testing.T) {
	root := installedFixture(t)
	app, err := newHandler(root)
	if err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(app)
	defer server.Close()
	response, err := http.Get(server.URL + "/?account=Design%20Partner")
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	page, err := io.ReadAll(response.Body)
	if err != nil {
		t.Fatal(err)
	}
	if response.StatusCode != http.StatusOK {
		t.Fatalf("page status %d", response.StatusCode)
	}
	for _, text := range []string{"Operations snapshot", "Design Partner", "1,284", "syn-stat", "/syntyr/css/syntyr.core.css"} {
		if !strings.Contains(string(page), text) {
			t.Errorf("missing %q in rendered page", text)
		}
	}

	styles, err := http.Get(server.URL + "/syntyr/css/syntyr.core.css")
	if err != nil {
		t.Fatal(err)
	}
	defer styles.Body.Close()
	responseCSS, err := io.ReadAll(styles.Body)
	if err != nil {
		t.Fatal(err)
	}
	sourceCSS, err := os.ReadFile(filepath.Join(root, "syntyr", "css", "syntyr.core.css"))
	if err != nil {
		t.Fatal(err)
	}
	if styles.StatusCode != http.StatusOK || string(responseCSS) != string(sourceCSS) {
		t.Fatalf("stylesheet does not match installed source: %d", styles.StatusCode)
	}
}

func TestHTMLTemplateEscapesUntrustedAccountName(t *testing.T) {
	app, err := newHandler(installedFixture(t))
	if err != nil {
		t.Fatal(err)
	}
	request := httptest.NewRequest(http.MethodGet, "/?account=%3Cscript%3Ealert(1)%3C%2Fscript%3E", nil)
	recorder := httptest.NewRecorder()
	app.ServeHTTP(recorder, request)
	markup := recorder.Body.String()
	if strings.Contains(markup, "<script>alert(1)</script>") {
		t.Fatal("untrusted input was rendered as executable HTML")
	}
	if !strings.Contains(markup, "&lt;script&gt;") {
		t.Fatal("untrusted input was not shown safely as text")
	}
}

func TestUnknownRouteReturnsNotFound(t *testing.T) {
	app, err := newHandler(installedFixture(t))
	if err != nil {
		t.Fatal(err)
	}
	recorder := httptest.NewRecorder()
	app.ServeHTTP(recorder, httptest.NewRequest(http.MethodGet, "/missing", nil))
	if recorder.Code != http.StatusNotFound {
		t.Fatalf("route returned %d", recorder.Code)
	}
}

func TestRequiresInstalledStylesheet(t *testing.T) {
	if _, err := newHandler(t.TempDir()); err == nil {
		t.Fatal("missing installed CSS must cause an actionable startup error")
	}
}
