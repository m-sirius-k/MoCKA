// mocka_sender.go
// MoCKA UTF-8 HTTP Gateway (Phase 3-A)
// 役割: PowerShell HTTP送信の完全置換。UTF-8関所の門番。
// ビルド: go build -o mocka_sender.exe mocka_sender.go
// 配置先: C:\Users\sirok\MoCKA\tools\mocka_sender.exe

package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
	"unicode/utf8"
)

const (
	version        = "1.0.0"
	defaultBase    = "http://127.0.0.1:5000"
	defaultTimeout = 10 * time.Second
)

// 出力JSON構造
type Result struct {
	OK       bool   `json:"ok"`
	Status   int    `json:"status"`
	Bytes    int    `json:"bytes"`
	Endpoint string `json:"endpoint"`
	Message  string `json:"message,omitempty"`
	Error    string `json:"error,omitempty"`
}

func printResult(r Result) {
	b, _ := json.Marshal(r)
	fmt.Println(string(b))
}

func printErr(msg string) {
	fmt.Fprintln(os.Stderr, "[mocka_sender] "+msg)
}

// BOM除去
func stripBOM(b []byte) []byte {
	if len(b) >= 3 && b[0] == 0xEF && b[1] == 0xBB && b[2] == 0xBF {
		return b[3:]
	}
	return b
}

// UTF-8検証
func validateUTF8(b []byte) bool {
	return utf8.Valid(b)
}

// HTTP送信
func send(endpoint, payload string, dryRun, verbose bool) int {
	raw := []byte(payload)
	raw = stripBOM(raw)

	if !validateUTF8(raw) {
		printErr("UTF-8 validation failed. Non-UTF-8 input rejected.")
		printResult(Result{OK: false, Endpoint: endpoint, Error: "invalid UTF-8"})
		return 4
	}

	// JSON整形確認（パースできるか）
	var jsonCheck interface{}
	if err := json.Unmarshal(raw, &jsonCheck); err != nil {
		printErr("Invalid JSON: " + err.Error())
		printResult(Result{OK: false, Endpoint: endpoint, Error: "invalid JSON: " + err.Error()})
		return 1
	}

	if verbose {
		printErr(fmt.Sprintf("→ Sending to %s (%d bytes)", endpoint, len(raw)))
		printErr(fmt.Sprintf("  Payload: %s", string(raw)))
	}

	if dryRun {
		printErr("[dry-run] Would POST to " + endpoint)
		printResult(Result{OK: true, Status: 0, Bytes: len(raw), Endpoint: endpoint, Message: "dry-run"})
		return 0
	}

	client := &http.Client{Timeout: defaultTimeout}
	req, err := http.NewRequest("POST", endpoint, bytes.NewReader(raw))
	if err != nil {
		printErr("Request build error: " + err.Error())
		printResult(Result{OK: false, Endpoint: endpoint, Error: err.Error()})
		return 2
	}

	req.Header.Set("Content-Type", "application/json; charset=utf-8")
	req.Header.Set("X-MoCKA-Sender", "mocka_sender/"+version)

	resp, err := client.Do(req)
	if err != nil {
		printErr("HTTP error: " + err.Error())
		printResult(Result{OK: false, Endpoint: endpoint, Error: err.Error()})
		return 3
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	ok := resp.StatusCode >= 200 && resp.StatusCode < 300

	if verbose {
		printErr(fmt.Sprintf("← Status: %d, Body: %s", resp.StatusCode, string(body)))
	}

	printResult(Result{
		OK:       ok,
		Status:   resp.StatusCode,
		Bytes:    len(raw),
		Endpoint: endpoint,
		Message:  string(body),
	})

	if !ok {
		return 3
	}
	return 0
}

// stdinから読み込み
func readStdin() (string, error) {
	b, err := io.ReadAll(os.Stdin)
	if err != nil {
		return "", err
	}
	return string(stripBOM(b)), nil
}

// ヘルスチェック
func check(endpoint string) int {
	client := &http.Client{Timeout: defaultTimeout}
	resp, err := client.Get(endpoint)
	if err != nil {
		printErr("Health check failed: " + err.Error())
		printResult(Result{OK: false, Endpoint: endpoint, Error: err.Error()})
		return 3
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	ok := resp.StatusCode >= 200 && resp.StatusCode < 300
	printResult(Result{
		OK:       ok,
		Status:   resp.StatusCode,
		Endpoint: endpoint,
		Message:  string(body),
	})
	if !ok {
		return 3
	}
	return 0
}

func usage() {
	fmt.Fprintf(os.Stderr, `mocka_sender v%s — MoCKA UTF-8 HTTP Gateway

Usage:
  mocka_sender send --endpoint <url> --json '<json>'
  mocka_sender send --endpoint <url> --file <path>
  mocka_sender send --endpoint <url> --stdin
  mocka_sender check --endpoint <url>

Shortcuts (base: %s):
  mocka_sender success '{"id":"E001","msg":"テスト"}'
  mocka_sender collect '{"url":"https://example.com","text":"内容"}'
  mocka_sender health

Options:
  --endpoint   Full URL (overrides shortcut)
  --json       JSON string
  --file       Path to JSON file
  --stdin      Read JSON from stdin
  --base       Base URL (default: %s)
  --dry-run    Print without sending
  --verbose    Show request/response details
  --version    Show version

Exit codes:
  0 = success
  1 = invalid arguments / bad JSON
  2 = I/O failure
  3 = HTTP failure
  4 = UTF-8 validation failure
`, version, defaultBase, defaultBase)
	os.Exit(1)
}

func main() {
	if len(os.Args) < 2 {
		usage()
	}

	// サブコマンド
	subcmd := os.Args[1]

	// ショートカット
	shortcuts := map[string]string{
		"success": "/success",
		"collect": "/collect",
		"health":  "/health",
	}

	sendCmd := flag.NewFlagSet("send", flag.ExitOnError)
	sendEndpoint := sendCmd.String("endpoint", "", "Full endpoint URL")
	sendJSON := sendCmd.String("json", "", "JSON payload string")
	sendFile := sendCmd.String("file", "", "Path to JSON file")
	sendStdin := sendCmd.Bool("stdin", false, "Read from stdin")
	sendBase := sendCmd.String("base", defaultBase, "Base URL")
	sendDry := sendCmd.Bool("dry-run", false, "Dry run")
	sendVerbose := sendCmd.Bool("verbose", false, "Verbose output")

	checkCmd := flag.NewFlagSet("check", flag.ExitOnError)
	checkEndpoint := checkCmd.String("endpoint", "", "Full endpoint URL")
	checkBase := checkCmd.String("base", defaultBase, "Base URL")

	switch subcmd {

	case "--version", "version":
		fmt.Println("mocka_sender v" + version)
		os.Exit(0)

	case "health":
		os.Exit(check(defaultBase + "/health"))

	// ショートカット: mocka_sender success '{...}'
	case "success", "collect":
		path, ok := shortcuts[subcmd]
		if !ok {
			usage()
		}
		if len(os.Args) < 3 {
			printErr("JSON payload required")
			os.Exit(1)
		}
		payload := strings.Join(os.Args[2:], " ")
		os.Exit(send(defaultBase+path, payload, false, false))

	case "send":
		sendCmd.Parse(os.Args[2:])
		endpoint := *sendEndpoint
		if endpoint == "" {
			printErr("--endpoint is required for send command")
			os.Exit(1)
		}
		if !strings.HasPrefix(endpoint, "http") {
			endpoint = *sendBase + endpoint
		}

		var payload string
		switch {
		case *sendJSON != "":
			payload = *sendJSON
		case *sendFile != "":
			b, err := os.ReadFile(*sendFile)
			if err != nil {
				printErr("File read error: " + err.Error())
				os.Exit(2)
			}
			payload = string(stripBOM(b))
		case *sendStdin:
			var err error
			payload, err = readStdin()
			if err != nil {
				printErr("Stdin read error: " + err.Error())
				os.Exit(2)
			}
		default:
			printErr("One of --json, --file, --stdin is required")
			os.Exit(1)
		}

		os.Exit(send(endpoint, payload, *sendDry, *sendVerbose))

	case "check":
		checkCmd.Parse(os.Args[2:])
		endpoint := *checkEndpoint
		if endpoint == "" {
			endpoint = *checkBase + "/health"
		}
		os.Exit(check(endpoint))

	default:
		printErr("Unknown command: " + subcmd)
		usage()
	}
}
