// SROTrac: nav helpers + members/activity filtering
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
      if (!drop.classList.contains('open')) { e.preventDefault(); drop.classList.add('open'); }
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

  // Members page
  var dataEl = document.getElementById('member-data');
  if (dataEl){
    var members = JSON.parse(dataEl.textContent);
    var rowsEl = document.getElementById('mrows');
    var countEl = document.getElementById('mcount');
    var q = '', f = 'ALL';
    var multi = {};
    members.forEach(function(m){ multi[m.n] = (multi[m.n]||0)+ (multi[m.n]?0:0); });
    var countByOrg = {};
    members.forEach(function(m){ countByOrg[m.n] = (countByOrg[m.n]||0)+1; });
    function render(){
      var out = '', shown = 0;
      var needle = q.toLowerCase();
      members.forEach(function(m){
        if (f === 'MULTI' && countByOrg[m.n] < 2) return;
        if (f !== 'ALL' && f !== 'MULTI' && m.s !== f) return;
        if (needle && m.n.toLowerCase().indexOf(needle) === -1) return;
        shown++;
        out += '<tr><td>'+m.n+'</td><td><span class="badge" style="--c:var(--accent)">'+m.s+'</span></td>'+
               '<td><span class="pill small">'+m.t+'</span></td>'+
               '<td class="linkcell"><a href="'+m.w+'" rel="noopener">'+m.w.replace(/^https?:\/\//,'')+'</a></td></tr>';
      });
      rowsEl.innerHTML = out || '<tr><td colspan="4">No matches.</td></tr>';
      countEl.textContent = shown + ' of ' + members.length + ' rows shown';
    }
    document.getElementById('mq').addEventListener('input', function(e){ q = e.target.value; render(); });
    chipFilter('#chips', function(v){ f = v; render(); });
    render();
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
        var badge = ['FACE','UFF','FIDC','SRPA'].indexOf(a.s) >= 0
          ? '<a class="badge" href="/sro-'+a.s.toLowerCase()+'.html">'+a.s+'</a>'
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
