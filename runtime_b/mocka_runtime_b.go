// MoCKA Runtime B — Go Implementation
// Phase 3: SQLite読み取り専用・軽量HTTPサーバー
// ポート: 5003（app.py=5000と独立）
//
// ビルド:
//   go mod init mocka_runtime_b
//   go get modernc.org/sqlite
//   go build -o mocka_runtime_b.exe mocka_runtime_b.go
//
// 実行:
//   mocka_runtime_b.exe
//   mocka_runtime_b.exe --port 5003 --db C:\Users\sirok\MoCKA\data\mocka_events.db

package main

import (
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"time"

	_ "modernc.org/sqlite"
)

// ============================================================
// 設定
// ============================================================
var (
	port   = flag.String("port", "5003", "HTTPポート番号")
	dbPath = flag.String("db", defaultDBPath(), "SQLiteDBパス")
)

func defaultDBPath() string {
	root := os.Getenv("MOCKA_ROOT")
	if root == "" {
		root = `C:\Users\sirok\MoCKA`
	}
	return filepath.Join(root, "data", "mocka_events.db")
}

// ============================================================
// データ構造
// ============================================================
type Event struct {
	EventID        string  `json:"event_id"`
	WhenTs         string  `json:"when"`
	WhoActor       string  `json:"who_actor"`
	WhatType       string  `json:"what_type"`
	WhereComponent string  `json:"where_component"`
	WherePath      string  `json:"where_path"`
	RiskLevel      string  `json:"risk_level"`
	Title          string  `json:"title"`
	ShortSummary   string  `json:"short_summary"`
	AiActor        string  `json:"ai_actor"`
	SessionID      string  `json:"session_id"`
	Severity       *int    `json:"severity"`
	PatternScore   *float64 `json:"pattern_score"`
	RecurrenceFlag int     `json:"recurrence_flag"`
	VerifiedBy     string  `json:"verified_by"`
	Source         string  `json:"_source"`
}

type HealthResponse struct {
	Status    string `json:"status"`
	Runtime   string `json:"runtime"`
	DB        string `json:"db"`
	DBExists  bool   `json:"db_exists"`
	EventCount int   `json:"event_count"`
	Timestamp string `json:"timestamp"`
}

type CountResponse struct {
	Count    int    `json:"count"`
	Filter   string `json:"filter,omitempty"`
	Runtime  string `json:"runtime"`
}

type EventsResponse struct {
	Events  []Event `json:"events"`
	Count   int     `json:"count"`
	Total   int     `json:"total"`
	Runtime string  `json:"runtime"`
}

// ============================================================
// DB接続
// ============================================================
func openDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite", *dbPath+"?mode=ro") // 読み取り専用
	if err != nil {
		return nil, err
	}
	db.SetMaxOpenConns(5)
	db.SetMaxIdleConns(2)
	return db, nil
}

func nullString(ns sql.NullString) string {
	if ns.Valid {
		return ns.String
	}
	return ""
}

func nullInt(ni sql.NullInt64) *int {
	if ni.Valid {
		v := int(ni.Int64)
		return &v
	}
	return nil
}

func nullFloat(nf sql.NullFloat64) *float64 {
	if nf.Valid {
		return &nf.Float64
	}
	return nil
}

// ============================================================
// ハンドラ
// ============================================================

// GET /b/health — 死活確認
func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	resp := HealthResponse{
		Runtime:   "go",
		DB:        *dbPath,
		DBExists:  false,
		EventCount: 0,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	if _, err := os.Stat(*dbPath); err == nil {
		resp.DBExists = true
		db, err := openDB()
		if err == nil {
			defer db.Close()
			db.QueryRow("SELECT COUNT(*) FROM events").Scan(&resp.EventCount)
			resp.Status = "ok"
		} else {
			resp.Status = "db_error"
		}
	} else {
		resp.Status = "db_not_found"
	}

	json.NewEncoder(w).Encode(resp)
}

// GET /b/count?what_type=incident&risk_level=critical — 件数
func countHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	db, err := openDB()
	if err != nil {
		http.Error(w, `{"error":"db_open_failed"}`, 500)
		return
	}
	defer db.Close()

	query := "SELECT COUNT(*) FROM events WHERE 1=1"
	args := []interface{}{}
	filter := ""

	if wt := r.URL.Query().Get("what_type"); wt != "" {
		query += " AND what_type = ?"
		args = append(args, wt)
		filter += "what_type=" + wt + " "
	}
	if rl := r.URL.Query().Get("risk_level"); rl != "" {
		query += " AND risk_level = ?"
		args = append(args, rl)
		filter += "risk_level=" + rl
	}

	var count int
	db.QueryRow(query, args...).Scan(&count)

	json.NewEncoder(w).Encode(CountResponse{
		Count:   count,
		Filter:  filter,
		Runtime: "go",
	})
}

// GET /b/events?limit=20&order=desc&what_type=incident — イベント一覧
func eventsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	db, err := openDB()
	if err != nil {
		http.Error(w, `{"error":"db_open_failed"}`, 500)
		return
	}
	defer db.Close()

	// パラメータ
	limit := 20
	if l := r.URL.Query().Get("limit"); l != "" {
		if n, err := strconv.Atoi(l); err == nil && n > 0 && n <= 1000 {
			limit = n
		}
	}
	order := "DESC"
	if r.URL.Query().Get("order") == "asc" {
		order = "ASC"
	}

	query := `SELECT event_id, when_ts, who_actor, what_type,
		where_component, where_path, risk_level, title, short_summary,
		COALESCE(ai_actor,''), COALESCE(session_id,''),
		severity, pattern_score, COALESCE(recurrence_flag,0),
		COALESCE(verified_by,''), COALESCE(_source,'')
		FROM events WHERE 1=1`
	args := []interface{}{}

	if wt := r.URL.Query().Get("what_type"); wt != "" {
		query += " AND what_type = ?"
		args = append(args, wt)
	}
	if rl := r.URL.Query().Get("risk_level"); rl != "" {
		query += " AND risk_level = ?"
		args = append(args, rl)
	}
	if kw := r.URL.Query().Get("q"); kw != "" {
		query += " AND (title LIKE ? OR short_summary LIKE ?)"
		args = append(args, "%"+kw+"%", "%"+kw+"%")
	}

	query += fmt.Sprintf(" ORDER BY when_ts %s LIMIT ?", order)
	args = append(args, limit)

	// 総件数
	var total int
	db.QueryRow("SELECT COUNT(*) FROM events").Scan(&total)

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, `{"error":"query_failed"}`, 500)
		return
	}
	defer rows.Close()

	events := []Event{}
	for rows.Next() {
		var e Event
		var whenTs, whoActor, whatType, whereComp, wherePath, riskLevel, title, shortSummary sql.NullString
		var severity sql.NullInt64
		var patternScore sql.NullFloat64

		rows.Scan(
			&e.EventID, &whenTs, &whoActor, &whatType,
			&whereComp, &wherePath, &riskLevel, &title, &shortSummary,
			&e.AiActor, &e.SessionID,
			&severity, &patternScore, &e.RecurrenceFlag,
			&e.VerifiedBy, &e.Source,
		)
		e.WhenTs = nullString(whenTs)
		e.WhoActor = nullString(whoActor)
		e.WhatType = nullString(whatType)
		e.WhereComponent = nullString(whereComp)
		e.WherePath = nullString(wherePath)
		e.RiskLevel = nullString(riskLevel)
		e.Title = nullString(title)
		e.ShortSummary = nullString(shortSummary)
		e.Severity = nullInt(severity)
		e.PatternScore = nullFloat(patternScore)
		events = append(events, e)
	}

	json.NewEncoder(w).Encode(EventsResponse{
		Events:  events,
		Count:   len(events),
		Total:   total,
		Runtime: "go",
	})
}

// ============================================================
// メイン
// ============================================================
func main() {
	flag.Parse()

	log.Printf("MoCKA Runtime B (Go) starting...")
	log.Printf("  DB:   %s", *dbPath)
	log.Printf("  Port: %s", *port)

	http.HandleFunc("/b/health", healthHandler)
	http.HandleFunc("/b/count",  countHandler)
	http.HandleFunc("/b/events", eventsHandler)

	// ルートへのアクセスにも応答
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"name":    "MoCKA Runtime B",
			"runtime": "go",
			"version": "1.0.0",
			"endpoints": "/b/health /b/count /b/events",
		})
	})

	addr := "127.0.0.1:" + *port
	log.Printf("Listening on http://%s", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
