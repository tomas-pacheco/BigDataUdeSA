"""
TUTORIAL DE BIG DATA
Tutorial 4, Parte II
"""

#pip install webdriver

# Es importante tener descargado el webdriver para Chrome (u otro navegador)
# https://sites.google.com/chromium.org/driver/getting-started

# Importamos paquetes
import os
from bs4 import BeautifulSoup #html parser
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')


main_dir = '/Users/tomaspacheco/Documents/GitHub/BigDataUdeSA/Tutorial_4/'
os.chdir(main_dir)

# Voy a buscar la página de Jumbo de gaseosas. La defino
url = 'https://www.jumbo.com.ar/Bebidas/Gaseosas'

# Abro el driver
driver = webdriver.Chrome(options=options)

# Abro la página en el driver
driver.get(url)

# Extraigo el html
html_source = driver.page_source

# Uso beautiful soup para 'parsearlo'
soup = BeautifulSoup(html_source, "html.parser")

# Busco todos los 'casilleros' de productos usando el id y la clase 
productos = soup.find_all('div', class_ = 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4')

# Defino df para los resultados
df = pd.DataFrame(columns=['marca', 'producto', 'precio_lista', 'precio_descuento'])


row = 0
# Para cada producto de la lista de productos
for prod in productos:
    
    # Extraigo la marca
    marca = prod.find('div', class_ = 'vtex-product-summary-2-x-productBrandContainer').text
    # Extraigo el nombre del producto
    producto = prod.find('span', class_ = 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body').text
    
    # Puede haber dos precios: lista y descuento, o solo lista
    try: # Le digo que intente buscar el precio de lista Y el de descuento. Si puede, buenísimo
        precio_lista = prod.find('div', class_ = 'jumboargentinaio-store-theme-2t-mVsKNpKjmCAEM_AMCQH').text
        precio_descuento = prod.find('div', class_ = 'jumboargentinaio-store-theme-1oaMy8g_TkKDcWOQsx5V2i').text
    except: # Si no puede, que fije el precio de descuento en missing
        precio_lista = prod.find('div', class_ = 'jumboargentinaio-store-theme-1oaMy8g_TkKDcWOQsx5V2i').text
        precio_descuento = ''  
    
    # Junto todo los elementos en una lista
    fila = [marca, producto, precio_lista, precio_descuento]    
    # Lo sumo a mi dataset original
    df.loc[row] = fila
    
    # Incremento el numero de fila
    row += 1
    
    
## Con esas mismas lineas, voy a hacer una funcion que tome como input el html de la pagina de Jumbo y devuelva un dataframe con los productos y sus precios

def get_prices(htmlcode):
    # Parse con beautiful soup
    soup = BeautifulSoup(htmlcode, "html.parser")

    # Busco los productos de la paginas
    productos = soup.find_all('div', class_ = 'vtex-search-result-3-x-galleryItem vtex-search-result-3-x-galleryItem--normal vtex-search-result-3-x-galleryItem--grid pa4')

    # Defino el data frame para resultados
    df = pd.DataFrame(columns=['marca', 'producto', 'precio_lista', 'precio_descuento'])

    # Corro el loop para extraer precios
    row = 0
    for prod in productos:
        marca = prod.find('div', class_ = 'vtex-product-summary-2-x-productBrandContainer').text
        producto = prod.find('span', class_ = 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body').text
        try:
            precio_lista = prod.find('div', class_ = 'jumboargentinaio-store-theme-2t-mVsKNpKjmCAEM_AMCQH').text
            precio_descuento = prod.find('div', class_ = 'jumboargentinaio-store-theme-1oaMy8g_TkKDcWOQsx5V2i').text
        except:
            precio_lista = prod.find('div', class_ = 'jumboargentinaio-store-theme-1oaMy8g_TkKDcWOQsx5V2i').text
            precio_descuento = ''  
        
        fila = [marca, producto, precio_lista, precio_descuento]    
        df.loc[row] = fila
        row += 1
    
    return(df)
        
    
# Lo pruebo con galletitas
url2 = 'https://www.jumbo.com.ar/almacen/desayuno-y-merienda/galletitas-dulces' 
driver.get(url2)

html_source = driver.page_source
df2 = get_prices(html_source)
# Funciona!

# Ahora vamos a ver de darle como input a python la categoria general y que busque por todas las paginas

# Categoria general. Cafés: https://www.jumbo.com.ar/almacen/desayuno-y-merienda/cafes?page=1
url_all = 'https://www.jumbo.com.ar/almacen/desayuno-y-merienda/cafes?page='

# Abro el driver
driver = webdriver.Chrome(options=options)

# Defino el data frame para guardar los resultados
df_final = pd.DataFrame(columns=['marca', 'producto', 'precio_lista', 'precio_descuento'])

for page in range(1, 1000):
    # Pagina a buscar (con el numero)
    path_temp = url_all + str(page)
    driver.get(path_temp)
    # Esperar 3 segundos
    time.sleep(5)
    
    # Scrolear hasta abajo como si fuese una persona    
    for i in range(0, 350, 5):
        driver.execute_script("window.scrollBy(0, 50);")
        time.sleep(0.05)
    
    # Extraigo el codigo fuente
    html_source = driver.page_source

    # Notar que cuando ya no hay mas páginas de un determinado producto
    # En la página dice "No se encontró ningún producto"
    
    # Si el texto de que no encontró ningún producot NO está en el html
    if 'No se encontró ningún producto' in html_source:
        # Llamo a la función get_prices
        df2 = get_prices(html_source)
        # Lo sumo al data frame 'df_final'
        df_final = pd.concat([df_final, df2])
        # Imprimo cantidad de productos de la página y total
        print(len(df2), len(df_final))
    # En caso de que el texto de que no encontró producto SI esté en el html
    else:
        # Termina el loop
        break

# Cierro el driver
driver.quit()
