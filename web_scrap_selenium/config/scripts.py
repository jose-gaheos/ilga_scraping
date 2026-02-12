

def get_script_inject_recapctha_token(token):
    return f"""
            var token = '{token}';
            var cfg = window.___grecaptcha_cfg.clients[0];
            
            // 1. Buscamos dinámicamente el objeto que tiene el callback
            var encontrado = false;
            for (var i in cfg) {{
                if (cfg[i] && cfg[i].F && cfg[i].F.callback) {{ // Basado en el hallazgo F.F
                    cfg[i].F.callback(token);
                    encontrado = true;
                    break;
                }}
                // Búsqueda genérica por si las letras cambian
                for (var j in cfg[i]) {{
                    if (cfg[i][j] && cfg[i][j].callback) {{
                        cfg[i][j].callback(token);
                        encontrado = true;
                        break;
                    }}
                }}
                if (encontrado) break;
            }}

           
        """

def get_script_inject_repactha_v3(token):
    return f"""
        var token = "{token}";
        var el = document.getElementById('g-recaptcha-response-100000') || document.querySelector('.g-recaptcha-response');
        
        if (el) {{
            el.value = token;
            // Notificar a Angular del cambio
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            
            // Ejecutar la lógica interna del SRI
            var cliente = ___grecaptcha_cfg.clients[100000];
            var mapa = cliente.l.__zone_symbol__value.l;
            mapa.get('d').call(cliente, {{"response": token}});
        }}
    """


#  // 2. Limpieza del botón para evitar el error de ruta %23
#             setTimeout(() => {{
#                 var btn = document.querySelector('button[type="submit"]');
#                 if (btn) {{
#                     btn.removeAttribute('routerlink');
#                     btn.disabled = false;
#                     btn.classList.remove('mat-mdc-button-disabled');
#                     btn.click();
#                 }}
#             }}, 500);