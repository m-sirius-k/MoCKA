(function() {
  var old = document.getElementById('mocka-badge');
  if (old) old.remove();
  var badge = document.createElement('div');
  badge.id = 'mocka-badge';
  badge.innerText = 'MOCKA: ONLINE / LEVER: ON';
  document.documentElement.appendChild(badge);
})();