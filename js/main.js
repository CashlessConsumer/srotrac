/// SROTrac: nav helpers + members/activity filtering
var SRO_KEYS = ["FACE", "UFF", "FIDC", "SRPA", "MFIN", "Sa-Dhan", "FEDAI", "Sahamati"];
(function(){
  // highlight current page
  function normPath(p){ return (p.length > 1 && p.charAt(p.length-1) === '/') ? p.slice(0, -1) : p; }
  var path = normPath(location.pathname) || '/';
  document.querySelectorAll('nav > a').forEach(function(a){
    var href = normPath(a.getAttribute('href')) || '/';
    if (href === path) a.classList.add('active'); else a.classList.remove('active');
  });

  // SRO dropdown: tap/click toggles on touch; hover handled by CSS on pointer devices
  var drop = document.querySelector('.nav-drop');
  if (drop) {
    drop.querySelector('.trigger').addEventListener('click', function(e){
      e.preventDefault();
      drop.classList.toggle('open');
    });
    document.addEventListener('click', function(e){
      if (!drop.contains(e.target)) drop.classList.remove('open');
    });
  }

  function chipFilter(containerSel, apply){
    var box = document.querySelector(containerSel);
    if (!box) return;
    box.addEventListener('click', function(e){
      var b = e.target.closest('.chip');
      if (!b) return;
      box.querySelectorAll('.chip').forEach(function(c){c.classList.remove('active');});
      b.classList.add('active');
      apply(b.dataset.f);
    });
  }

  // Members page: org-grouped rows, multi-select SRO + type chips, URL-hash state
  var dataEl = document.getElementById('member-data');
  if (dataEl){
    var members = JSON.parse(dataEl.textContent);
    var rowsEl = document.getElementById('mrows');
    var countEl = document.getElementById('mcount');
    var q = '', sroSel = new Set(), tySel = new Set(), multi = false;

    function parseHash(){
      var h = location.hash.replace(/^#/, '');
      if (!h){ q=''; sroSel.clear(); tySel.clear(); multi=false; return; }
      var parts = {};
      h.split('&').forEach(function(kv){ var p = kv.split('='); parts[p[0]] = decodeURIComponent(p[1]||''); });
      q = parts.q || '';
      sroSel = new Set((parts.sro||'').split(',').filter(Boolean).map(function(v){
        var k = v.toLowerCase();
        var hit = SRO_KEYS.filter(function(K){ return K.toLowerCase() === k; })[0];
        return hit || v;
      }));
      tySel = new Set((parts.ty||'').split(',').filter(Boolean));
      multi = parts.multi === '1';
      var iq = document.getElementById('mq'); if (iq) iq.value = q;
    }
    function writeHash(){
      var h = [];
      if (q) h.push('q='+encodeURIComponent(q));
      if (sroSel.size) h.push('sro='+Array.from(sroSel).join(','));
      if (tySel.size) h.push('ty='+Array.from(tySel).join(','));
      if (multi) h.push('multi=1');
      var newHash = h.length ? '#'+h.join('&') : '';
      if (location.hash !== newHash) history.replaceState(null, '', location.pathname + newHash);
    }
    function syncChips(){
      document.querySelectorAll('#srochips .chip').forEach(function(c){
        var v = c.dataset.sro;
        c.classList.toggle('active',
          v === 'MULTI' ? multi : (v === 'ALL' ? sroSel.size===0 && !multi : sroSel.has(v)));
      });
      document.querySelectorAll('#typechips .chip').forEach(function(c){
        var v = c.dataset.ty;
        c.classList.toggle('active', v === 'ALL' ? tySel.size===0 : tySel.has(v));
      });
    }
    function match(m){
      if (multi && m.s.length < 2) return false;
      if (sroSel.size && !m.s.some(function(x){ return sroSel.has(x) || sroSel.has(x.toLowerCase()); })) return false;
      if (tySel.size && !tySel.has(m.ty)) return false;
      if (q && m.n.toLowerCase().indexOf(q.toLowerCase()) === -1) return false;
      return true;
    }
    function render(){
      var out = '', shown = 0;
      members.forEach(function(m){
        if (!match(m)) return;
        shown++;
        var badges = m.s.map(function(x){
          return '<a class="badge" style="--c:'+(m.c[x]||'#57534e')+'" href="/sro-'+x.toLowerCase().replace(' ','-')+'.html">'+x+'</a>';
        }).join(' ');
        var link = m.w ? '<a href="'+m.w+'" rel="noopener">'+m.w.replace(/^https?:\/\//,'')+'</a>' : '<span class="muted">—</span>';
        out += '<tr><td>'+m.n+'</td><td><span class="pill small">'+m.t+'</span></td><td>'+badges+'</td><td class="linkcell">'+link+'</td></tr>';
      });
      rowsEl.innerHTML = out || '<tr><td colspan="4">No matches.</td></tr>';
      countEl.textContent = shown + ' of ' + members.length + ' organisations shown';
    }
    document.getElementById('mq').addEventListener('input', function(e){ q = e.target.value; writeHash(); render(); });
    document.querySelector('#srochips').addEventListener('click', function(e){
      var b = e.target.closest('.chip'); if (!b) return;
      var v = b.dataset.sro;
      if (v === 'ALL'){ sroSel.clear(); multi = false; }
      else if (v === 'MULTI'){ multi = !multi; }
      else { sroSel.has(v) ? sroSel.delete(v) : sroSel.add(v); }
      writeHash(); syncChips(); render();
    });
    document.querySelector('#typechips').addEventListener('click', function(e){
      var b = e.target.closest('.chip'); if (!b) return;
      var v = b.dataset.ty;
      if (v === 'ALL'){ tySel.clear(); }
      else { tySel.has(v) ? tySel.delete(v) : tySel.add(v); }
      writeHash(); syncChips(); render();
    });
    window.addEventListener('hashchange', function(){ parseHash(); syncChips(); render(); });
    parseHash(); syncChips(); render();
  }

  // Activity page
  var actEl = document.getElementById('activity-data');
  if (actEl){
    var acts = JSON.parse(actEl.textContent);
    var list = document.getElementById('alist');
    var f2 = 'ALL';
    function render2(){
      var out = '';
      acts.forEach(function(a){
        if (f2 !== 'ALL' && a.t !== f2) return;
        var sl = a.s.toLowerCase();
        var badge = SRO_KEYS.indexOf(a.s) >= 0
          ? '<a class="badge" href="/sro-'+sl.replace(/\s+/g,'-')+'.html">'+a.s+'</a>'
          : '<span class="badge">RBI</span>';
        out += '<div class="card"><p class="meta"><span class="date">'+a.d+'</span> '+badge+
               ' <span class="pill small">'+a.t+'</span></p><h3><a href="'+a.u+'" rel="noopener">'+a.h+'</a></h3><p>'+a.x+'</p></div>';
      });
      list.innerHTML = out;
    }
    chipFilter('#achips', function(v){ f2 = v; render2(); });
    render2();
  }
})();
