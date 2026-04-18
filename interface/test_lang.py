from language_detector import LanguageDetector
from essence_classifier import classify

d = LanguageDetector()
tests = [
    'なぜそうなる？動かない。また同じ。',
    '失敗は資産になる。地道に記録する。',
    'router.pyを修正した。',
    '勝手に変えるな。最悪。時間の無駄。',
]
for t in tests:
    cat = classify(t)
    det = d.analyze(t)
    print('[' + det['level'] + '] ' + cat + ' | ' + t[:30])
