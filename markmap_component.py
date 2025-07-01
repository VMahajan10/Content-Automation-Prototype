import streamlit as st
import streamlit.components.v1 as components

def markmap(md: str, height=600):
    markmap_js = "https://cdn.jsdelivr.net/npm/markmap-autoloader"
    html = f"""
    <html>
    <head>
      <script src="{markmap_js}"></script>
    </head>
    <body>
      <svg id="mindmap"></svg>
      <script>
        window.markmap.autoLoader.renderAll();
      </script>
      <script type="text/markdown" id="markmap-data">
{md}
      </script>
    </body>
    </html>
    """
    components.html(html, height=height)