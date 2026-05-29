// i18n.js — PHI OS 多言語対応 (ja/en/zh/ko/es)
'use strict';

const I18N = {
  ja: {
    btn_commit:       'セッションを保存',
    btn_restore:      '前回を復元',
    btn_toggle_panel: 'パネル切り換え',
    btn_lang:         '言語',
    btn_settings:     '設定',
    btn_export:       'エクスポート',
    btn_manual:       'マニュアル',
    status_standalone: 'スタンドアロン動作中',
    status_connected:  'MoCKA接続中',
    status_committing: '保存中...',
    status_saved:      '保存完了',
    status_restored:   '復元しました',
    status_error:      'エラーが発生しました',
    label_facts:      '新しい事実',
    label_decisions:  '決定事項',
    label_todos:      '未完了タスク',
    label_tensions:   '違和感・疑問',
    label_next_hook:  '次回の起動ポイント',
    mem_copy:         'Memoryブロックをコピー',
    mem_env:          '環境制約として記録',
    mem_error:        'エラー解決策として記録',
    mem_decision:     '決定事項として記録',
    err_storage_full: 'ストレージが満杯です。古いデータを削除してください。',
    err_no_content:   '保存するコンテンツがありません',
    err_inject_fail:  '注入に失敗しました',
    man_what_is:      'PHI OSとは',
    man_how_commit:   '保存の仕組み',
    man_how_restore:  '復元の仕組み',
    man_mode_switch:  'モード切り換え',
    man_lang_switch:  '言語切り換え',
    man_troubleshoot: 'トラブルシューティング',
  },
  en: {
    btn_commit:       'Save Session',
    btn_restore:      'Restore Last',
    btn_toggle_panel: 'Toggle Panel',
    btn_lang:         'Language',
    btn_settings:     'Settings',
    btn_export:       'Export',
    btn_manual:       'Manual',
    status_standalone: 'Standalone Mode',
    status_connected:  'MoCKA Connected',
    status_committing: 'Saving...',
    status_saved:      'Saved',
    status_restored:   'Restored',
    status_error:      'Error occurred',
    label_facts:      'New Facts',
    label_decisions:  'Decisions',
    label_todos:      'Pending TODOs',
    label_tensions:   'Tensions / Doubts',
    label_next_hook:  'Next Session Hook',
    mem_copy:         'Copy Memory Block',
    mem_env:          'Record as Environment Constraint',
    mem_error:        'Record as Error Solution',
    mem_decision:     'Record as Decision',
    err_storage_full: 'Storage is full. Please delete old data.',
    err_no_content:   'No content to save',
    err_inject_fail:  'Injection failed',
    man_what_is:      'What is PHI OS',
    man_how_commit:   'How Saving Works',
    man_how_restore:  'How Restore Works',
    man_mode_switch:  'Mode Switching',
    man_lang_switch:  'Language Switching',
    man_troubleshoot: 'Troubleshooting',
  },
  zh: {
    btn_commit:       '保存会话',
    btn_restore:      '恢复上次',
    btn_toggle_panel: '切换面板',
    btn_lang:         '语言',
    btn_settings:     '设置',
    btn_export:       '导出',
    btn_manual:       '手册',
    status_standalone: '独立模式',
    status_connected:  'MoCKA已连接',
    status_committing: '保存中...',
    status_saved:      '已保存',
    status_restored:   '已恢复',
    status_error:      '发生错误',
    label_facts:      '新事实',
    label_decisions:  '决策',
    label_todos:      '待办事项',
    label_tensions:   '疑虑·问题',
    label_next_hook:  '下次启动点',
    mem_copy:         '复制Memory块',
    mem_env:          '记录为环境约束',
    mem_error:        '记录为错误解决方案',
    mem_decision:     '记录为决策',
    err_storage_full: '存储已满，请删除旧数据。',
    err_no_content:   '没有可保存的内容',
    err_inject_fail:  '注入失败',
    man_what_is:      'PHI OS是什么',
    man_how_commit:   '保存机制',
    man_how_restore:  '恢复机制',
    man_mode_switch:  '模式切换',
    man_lang_switch:  '语言切换',
    man_troubleshoot: '故障排除',
  },
  ko: {
    btn_commit:       '세션 저장',
    btn_restore:      '이전 복원',
    btn_toggle_panel: '패널 전환',
    btn_lang:         '언어',
    btn_settings:     '설정',
    btn_export:       '내보내기',
    btn_manual:       '매뉴얼',
    status_standalone: '독립 실행 모드',
    status_connected:  'MoCKA 연결됨',
    status_committing: '저장 중...',
    status_saved:      '저장 완료',
    status_restored:   '복원 완료',
    status_error:      '오류가 발생했습니다',
    label_facts:      '새로운 사실',
    label_decisions:  '결정 사항',
    label_todos:      '미완료 태스크',
    label_tensions:   '의문점·불안요소',
    label_next_hook:  '다음 세션 시작점',
    mem_copy:         'Memory 블록 복사',
    mem_env:          '환경 제약으로 기록',
    mem_error:        '오류 해결책으로 기록',
    mem_decision:     '결정 사항으로 기록',
    err_storage_full: '저장소가 가득 찼습니다. 이전 데이터를 삭제하세요.',
    err_no_content:   '저장할 내용이 없습니다',
    err_inject_fail:  '주입에 실패했습니다',
    man_what_is:      'PHI OS란',
    man_how_commit:   '저장 방식',
    man_how_restore:  '복원 방식',
    man_mode_switch:  '모드 전환',
    man_lang_switch:  '언어 전환',
    man_troubleshoot: '문제 해결',
  },
  es: {
    btn_commit:       'Guardar sesión',
    btn_restore:      'Restaurar última',
    btn_toggle_panel: 'Cambiar panel',
    btn_lang:         'Idioma',
    btn_settings:     'Configuración',
    btn_export:       'Exportar',
    btn_manual:       'Manual',
    status_standalone: 'Modo independiente',
    status_connected:  'MoCKA conectado',
    status_committing: 'Guardando...',
    status_saved:      'Guardado',
    status_restored:   'Restaurado',
    status_error:      'Se produjo un error',
    label_facts:      'Nuevos hechos',
    label_decisions:  'Decisiones',
    label_todos:      'Tareas pendientes',
    label_tensions:   'Dudas·Anomalías',
    label_next_hook:  'Punto de inicio siguiente',
    mem_copy:         'Copiar bloque Memory',
    mem_env:          'Registrar como restricción de entorno',
    mem_error:        'Registrar como solución de error',
    mem_decision:     'Registrar como decisión',
    err_storage_full: 'El almacenamiento está lleno. Elimine datos antiguos.',
    err_no_content:   'No hay contenido para guardar',
    err_inject_fail:  'Error de inyección',
    man_what_is:      'Qué es PHI OS',
    man_how_commit:   'Cómo funciona el guardado',
    man_how_restore:  'Cómo funciona la restauración',
    man_mode_switch:  'Cambio de modo',
    man_lang_switch:  'Cambio de idioma',
    man_troubleshoot: 'Solución de problemas',
  },
};

const SUPPORTED_LANGS = ['ja', 'en', 'zh', 'ko', 'es'];
let currentLang = 'ja';

export function t(key) {
  return I18N[currentLang]?.[key] || I18N['en']?.[key] || key;
}

export async function initI18n() {
  try {
    const { phi_lang } = await chrome.storage.local.get('phi_lang');
    currentLang = phi_lang || detectBrowserLang() || 'ja';
  } catch (e) {
    currentLang = 'ja';
  }
  applyI18n();
}

export async function setLang(lang) {
  if (!SUPPORTED_LANGS.includes(lang)) return;
  currentLang = lang;
  try {
    await chrome.storage.local.set({ phi_lang: lang });
  } catch (e) {
    // storage unavailable in some contexts
  }
  applyI18n();
}

export function getLang() {
  return currentLang;
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
}

function detectBrowserLang() {
  const lang = navigator.language?.slice(0, 2);
  const map = { ja: 'ja', en: 'en', zh: 'zh', ko: 'ko', es: 'es' };
  return map[lang] || null;
}
