/* Modo juego de la web de Eduardo Merino.
   Todo se guarda en este dispositivo (localStorage): sin cuentas ni datos personales. */
(function () {
  const CLAVE = "em-progreso-v1";
  // juego:inicio (lo rellena herramientas/generar.py desde contenido.json)
  const PUNTOS = {"calibre": 10, "micrometro-centesimal": 15, "micrometro-milesimal": 20};
  const NOMBRES = {"calibre": "Calibre", "micrometro-centesimal": "Micrómetro 0,01", "micrometro-milesimal": "Micrómetro 0,001"};
  const INSTRUMENTOS = ["calibre", "micrometro-centesimal", "micrometro-milesimal"];
  // juego:fin
  const NIVELES = [
    { id: "aprendiz", nombre: "Aprendiz", desde: 0, icono: "🔧" },
    { id: "oficial", nombre: "Oficial", desde: 300, icono: "🛠️" },
    { id: "maestro", nombre: "Maestro", desde: 1000, icono: "🏅" },
    { id: "elite", nombre: "Élite", desde: 2500, icono: "👑" }
  ];
  const ac = (p, id) => (p.inst[id] || {}).a || 0;
  const INSIGNIAS = [
    { id: "primera", icono: "🎯", nombre: "Primera medida", texto: "Acierta tu primera medida.", ok: p => p.aciertos >= 1 },
    { id: "racha10", icono: "🔥", nombre: "Pulso firme", texto: "10 aciertos seguidos sin fallar.", ok: p => p.mejorRacha >= 10 },
    { id: "racha25", icono: "⚡", nombre: "Imparable", texto: "25 aciertos seguidos sin fallar.", ok: p => p.mejorRacha >= 25 },
    { id: "nonio", icono: "📏", nombre: "Maestro del nonio", texto: "25 aciertos con el calibre.", ok: p => ac(p, "calibre") >= 25 },
    { id: "centesima", icono: "🔩", nombre: "Centésima exacta", texto: "25 aciertos con el micrómetro centesimal.", ok: p => ac(p, "micrometro-centesimal") >= 25 },
    { id: "milesimal", icono: "⚙️", nombre: "Dominio del milesimal", texto: "25 aciertos con el micrómetro milesimal.", ok: p => ac(p, "micrometro-milesimal") >= 25 },
    { id: "completo", icono: "🧰", nombre: "Caja completa", texto: "Acierta con todos los instrumentos de medida.", ok: p => INSTRUMENTOS.every(id => ac(p, id) >= 1) },
    { id: "cien", icono: "💯", nombre: "Cien medidas", texto: "100 aciertos en total.", ok: p => p.aciertos >= 100 },
    { id: "dias3", icono: "📅", nombre: "Constancia", texto: "Practica 3 días seguidos.", ok: p => p.mejorRachaDias >= 3 },
    { id: "dias7", icono: "🗓️", nombre: "Una semana", texto: "Practica 7 días seguidos.", ok: p => p.mejorRachaDias >= 7 },
    { id: "dias30", icono: "🏆", nombre: "Día a día", texto: "Practica 30 días seguidos. La élite se construye día a día.", ok: p => p.mejorRachaDias >= 30 }
  ];

  const hoy = (d = new Date()) => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  const diaAntes = s => { const d = new Date(s + "T12:00:00"); d.setDate(d.getDate() - 1); return hoy(d); };

  function vacio() { return { v: 1, puntos: 0, aciertos: 0, intentos: 0, racha: 0, mejorRacha: 0, dias: [], mejorRachaDias: 0, inst: {} }; }
  function normalizar(p) {
    const b = vacio();
    if (!p || typeof p !== "object") return b;
    for (const k in b) if (typeof p[k] === typeof b[k] && (Array.isArray(b[k]) === Array.isArray(p[k]))) b[k] = p[k];
    b.dias = b.dias.filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort().slice(-400);
    return b;
  }
  function leer() { try { return normalizar(JSON.parse(localStorage.getItem(CLAVE))); } catch (e) { return vacio(); } }
  function guardar(p) { try { localStorage.setItem(CLAVE, JSON.stringify(p)); } catch (e) {} }

  // Días seguidos de práctica que llegan hasta hoy (o hasta ayer, si hoy aún no has practicado)
  function rachaDias(p) {
    const set = new Set(p.dias);
    let d = set.has(hoy()) ? hoy() : diaAntes(hoy()), n = 0;
    while (set.has(d)) { n++; d = diaAntes(d); }
    return n;
  }
  function nivel(p) {
    let i = 0;
    while (i + 1 < NIVELES.length && p.puntos >= NIVELES[i + 1].desde) i++;
    const sig = NIVELES[i + 1];
    return { ...NIVELES[i], indice: i, siguiente: sig || null,
             avance: sig ? (p.puntos - NIVELES[i].desde) / (sig.desde - NIVELES[i].desde) : 1 };
  }
  const ganadas = p => INSIGNIAS.filter(x => x.ok(p)).map(x => x.id);

  // Lo llaman los instrumentos al comprobar un reto. Devuelve los avisos que mostrar.
  function apuntar(id, ok) {
    const p = leer(), antesIns = ganadas(p), antesNiv = nivel(p).indice;
    const i = p.inst[id] = Object.assign({ a: 0, n: 0, r: 0, mr: 0 }, p.inst[id]);
    p.intentos++; i.n++;
    const avisos = [];
    if (ok) {
      let pts = PUNTOS[id] || 10;
      p.aciertos++; i.a++; p.racha++; i.r++;
      p.mejorRacha = Math.max(p.mejorRacha, p.racha); i.mr = Math.max(i.mr, i.r);
      if (p.racha % 5 === 0) pts += 5 * (p.racha / 5);           // premio por racha
      p.puntos += pts;
      if (!p.dias.includes(hoy())) { p.dias.push(hoy()); p.dias = p.dias.slice(-400); }
      p.mejorRachaDias = Math.max(p.mejorRachaDias, rachaDias(p));
      avisos.push(`+${pts} puntos`);
    } else { p.racha = 0; i.r = 0; }
    guardar(p);
    const niv = nivel(p);
    if (niv.indice > antesNiv) avisos.push(`${niv.icono} ¡Nuevo nivel: ${niv.nombre}!`);
    ganadas(p).filter(x => !antesIns.includes(x)).forEach(x => {
      const ins = INSIGNIAS.find(y => y.id === x); avisos.push(`${ins.icono} Insignia: ${ins.nombre}`);
    });
    return avisos;
  }

  function exportar() {
    const blob = new Blob([JSON.stringify({ app: "eduardo-merino", ...leer() }, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = `progreso-eduardo-merino-${hoy()}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  function importar(texto) {
    const d = JSON.parse(texto);
    if (!d || d.app !== "eduardo-merino") throw new Error("Ese archivo no es un progreso de esta web.");
    guardar(normalizar(d));
  }
  function borrar() { try { localStorage.removeItem(CLAVE); } catch (e) {} }

  window.EMJuego = { hoy, leer, apuntar, nivel, rachaDias, ganadas, exportar, importar, borrar, INSIGNIAS, NIVELES, NOMBRES };
})();
