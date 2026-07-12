# GL7_RUNTIME_ISOLATION_PLAN

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 計画のみ、実行(commit/restart)は未実施

目的: GL7-VALIDATION-MISSING-BUG(`mocka_mcp_server.py`、title/description/author空文字reject)の修正を、AUTO_SEAL Pack1(`app.py`/`watchdog_mocka.py`/`data/MOCKA_TODO_ACTIVE.json`)を巻き込まずにruntimeへ反映する方法を確認する。

## 重要な訂正

前回までの報告で「`mocka_mcp_server.py`を再起動するとPack1の未commit変更(app.py/watchdog_mocka.py)も本番稼働へ反映されてしまう」と述べていましたが、**これは誤りでした。訂正します。**

`MoCKA-START.bat`(67-68行)を確認したところ、以下の通り**完全に独立した別プロセス**として起動されています。

```
67行: "MoCKA-APP" タブ  → python app.py        (auto_audit_loop等、Pack1対象)
68行: "MoCKA-MCP" タブ  → python mocka_mcp_server.py (GL7対象)
```

`mocka_mcp_server.py`は`app.py`/`watchdog_mocka.py`をimportしておらず(grep確認済み、依存なし)、両者はOSレベルで独立したPythonプロセスです。**したがって`mocka_mcp_server.py`だけを再起動しても、`app.py`の未commit変更(AUTO_SEAL Pack1)がruntimeへ反映されることはありません。** 巻き込みリスクは実質存在しません(watchdog_mocka.pyは`MoCKA-START.bat`に記載がなく、起動経路自体が別途確認を要する)。

## branch分離可否

不要と判断。GL7の修正は`mocka_mcp_server.py`1ファイルに閉じており(509-522行付近)、Pack1の対象3ファイルとのファイル重複・import依存のいずれも存在しない(`git diff --stat`で確認済み、コード上の依存もgrep確認済みでゼロ件)。よってbranch/worktreeを使わずとも、`mocka_git_safe_commit(paths=["mocka_mcp_server.py"], message=..., push=False)`で単独commitすればコミット単位の分離は達成できる。

## cherry-pick対象commit

現時点でGL7修正はworking tree上の未commit変更のみで、既存commitは存在しない(cherry-pick元がない)。上記の単独commitを作成すれば、それ自体が完結したcherry-pick可能な単位になる(他ブランチへ後から持っていく必要が生じた場合に備える)。

## runtime反映手順

1. `mocka_git_safe_commit(paths=["mocka_mcp_server.py"], ...)`でGL7修正のみをcommit(Pack1とは別のDecision Record・別のcommitとする)
2. CLAUDE.md必須手順に従い、`data/tic/mcp_schema_hash.json`のハッシュ更新を実施
3. 「MoCKA-MCP」タブ(mocka_mcp_server.pyプロセス)のみを再起動。「MoCKA-APP」タブ(app.py)・watchdog_mocka.pyには一切触れない
4. 再起動後、GL7_FIX_VERIFY_TEST相当の再検証(空title/description/authorでの`mocka_write_event`呼び出しが`gate_rejected`を返すことを確認)

**付随する論点:** `mocka_mcp_server.py`は今回セッション中`Session terminated`のまま復旧していないMCPセッションの実体でもある。このプロセスを再起動すれば、GL7反映と同時にMCPセッション復旧の可能性もある。ただし稼働中プロセスの再起動は影響範囲のある操作のため、実行はきむら博士の明示判断を経てから行う。

## rollback方法

GL7単独commitをgit revertするか、`mocka_mcp_server.py`を直前バージョンへ戻す。ファイル依存がPack1とゼロであるため、rollbackもPack1の状態に一切影響しない。`mcp_schema_hash.json`も併せて旧ハッシュへ戻す必要がある(CLAUDE.md必須手順の対称操作)。

## 結論

GL7とAUTO_SEAL Pack1は、commit単位・プロセス単位いずれでも完全に分離可能。branch/cherry-pickのような重い機構は不要で、単独commit+「MoCKA-MCP」タブのみの再起動で足りる。実行(commit・再起動とも)はAUTO_SEAL Pack1完了後、きむら博士の承認を経て行う。
