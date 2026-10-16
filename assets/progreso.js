/* Página "Mi progreso": nivel, racha diaria, insignias y copia de seguridad. */
(function () {
  const J = window.EMJuego, $ = id => document.getElementById(id);
  const fmt = n => n.toLocaleString("es-ES");

  function pintar() {
    const p = J.leer(), niv = J.nivel(p), dias = J.rachaDias(p), ganadas = J.ganadas(p);
    $("nivelIcono").textContent = niv.icono;
    $("nivelNombre").textContent = niv.nombre;
    $("puntos").textContent = fmt(p.puntos);
    $("barra").style.width = Math.round(niv.avance * 100) + "%";
    $("siguiente").textContent = niv.siguiente
      ? `Te faltan ${fmt(niv.siguiente.desde - p.puntos)} puntos para ${niv.siguiente.nombre}.`
      : "Has llegado a lo más alto. Ahora, a mantenerlo día a día.";
    $("rachaDias").textContent = dias;
    $("rachaTexto").textContent = dias === 0 ? "Acierta un reto hoy para empezar tu racha."
      : p.dias.includes(J.hoy()) ? "¡Hoy ya has practicado!" : "Practica hoy para no perder la racha.";
    $("diasTxt").textContent = dias === 1 ? "día" : "días";
    $("mejorDias").textContent = p.mejorRachaDias + (p.mejorRachaDias === 1 ? " día" : " días");
    $("aciertos").textContent = fmt(p.aciertos);
    $("precision").textContent = p.intentos ? Math.round(100 * p.aciertos / p.intentos) + " %" : "—";
    $("mejorRacha").textContent = p.mejorRacha;

    const filas = Object.keys(J.NOMBRES).map(id => {
      const i = p.inst[id] || { a: 0, n: 0, mr: 0 };
      return `<tr><td>${J.NOMBRES[id]}</td><td>${i.a}</td><td>${i.n ? Math.round(100 * i.a / i.n) + " %" : "—"}</td><td>${i.mr}</td></tr>`;
    }).join("");
    $("tabla").innerHTML = filas;

    $("insignias").innerHTML = J.INSIGNIAS.map(x => {
      const ok = ganadas.includes(x.id);
      return `<div class="insignia${ok ? " ok" : ""}" title="${ok ? "Conseguida" : "Por conseguir"}">
        <span class="ico">${ok ? x.icono : "🔒"}</span><b>${x.nombre}</b><small>${x.texto}</small></div>`;
    }).join("");
    $("cuentaIns").textContent = `${ganadas.length} de ${J.INSIGNIAS.length}`;
  }

  $("bExportar").onclick = () => J.exportar();
  $("fImportar").onchange = e => {
    const f = e.target.files[0]; if (!f) return;
    f.text().then(t => { J.importar(t); pintar(); aviso("Progreso recuperado."); })
      .catch(err => aviso(err.message || "No se ha podido leer el archivo."));
    e.target.value = "";
  };
  $("bBorrar").onclick = () => {
    if (confirm("¿Seguro que quieres borrar todo tu progreso de este dispositivo? No se puede deshacer.")) { J.borrar(); pintar(); aviso("Progreso borrado."); }
  };
  function aviso(t) { const a = $("aviso"); a.textContent = t; a.hidden = false; setTimeout(() => a.hidden = true, 4000); }
  pintar();
})();
