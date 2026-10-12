# <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">PokeWrap<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png" alt="Texto alternativo" width="20">

[English](README.md) | **Español**

> Wrapper asíncrono, tipado y con caché para [PokeAPI](https://pokeapi.co).

[![Versión PyPI](https://img.shields.io/pypi/v/poke-wrap-client.svg)](https://pypi.org/project/poke-wrap-client/)
[![Versiones de Python](https://img.shields.io/pypi/pyversions/poke-wrap-client.svg)](https://pypi.org/project/poke-wrap-client/)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tipado](https://img.shields.io/badge/typing-typed-blue.svg)](https://peps.python.org/pep-0561/)

PokeWrap entrega **modelos de dominio tipados** en lugar de diccionarios
crudos, así escribes `pokemon.stats.total` en vez de
`data["stats"][3]["base_stat"]`. Cachea cada respuesta localmente para
respetar la política de uso justo de PokeAPI, e hidrata referencias solo
cuando se lo pides — nunca por sorpresa.

## Características

- 🚀 **Async-first**, construido sobre [`httpx`](https://www.python-httpx.org/).
- 🧬 **Modelos tipados** con [`Pydantic v2`](https://docs.pydantic.dev/) para autocompletado completo.
- 🗂️ **Caché local** vía [`hishel`](https://hishel.com/) (SQLite, compatible con RFC 9111).
- 🎯 **Hidratación controlada** — resuelve habilidades y tipos solo cuando lo pidas.
- 🐍 **Python 3.12+** con marcador de tipado PEP 561.

## Instalación

```bash
pip install poke-wrap-client
```

O con `uv`:

```bash
uv add poke-wrap-client
```

## Inicio rápido

```python
import asyncio
from poke_wrap import AsyncPokeAPIClient

async def main() -> None:
    async with AsyncPokeAPIClient() as client:
        pikachu = await client.get_pokemon("pikachu")
        print(pikachu["name"], pikachu["id"])
        # pikachu 25

asyncio.run(main())
```

`get_pokemon` devuelve el **JSON crudo** como diccionario — misma forma que
la respuesta de PokeAPI. Es una vía de escape para usuarios que quieren
control total.

## Modelos de dominio tipados

Para la mayoría de usuarios, la API de dominio es lo que quieren:

```python
from poke_wrap import AsyncPokeAPIClient

async with AsyncPokeAPIClient() as client:
    pokemon = await client.get_pokemon_domain("pikachu")

    print(pokemon.name)             # "pikachu"
    print(pokemon.height_m)         # 0.4  (convertido de decímetros)
    print(pokemon.weight_kg)        # 6.0  (convertido de hectogramos)
    print(pokemon.types)            # [<PokemonType.ELECTRIC: 'electric'>]
    print(pokemon.stats.total)      # 320
    print(pokemon.is_dual_type)     # False
```

Todo está tipado: tu editor autocompleta `pokemon.stats.attack` y marca
`pokemon.stats.attak` antes de que ejecutes el código.

## Hidratación: paga solo por lo que uses

Por defecto, referencias como habilidades y tipos son ligeras (nombre + URL).
Usa `get_pokemon_detailed` cuando necesites el payload completo:

```python
async with AsyncPokeAPIClient() as client:
    detailed = await client.get_pokemon_detailed("mewtwo")

    print(detailed.pokemon.name)              # "mewtwo"
    print(detailed.abilities[0].name)         # "pressure"
    print(detailed.abilities[0].effect)       # "Raises the PP usage..."
    print(detailed.types[0].name)             # <PokemonType.PSYCHIC: 'psychic'>
    print(detailed.types[0].damage_relations.double_damage_from)
    # [<PokemonType.BUG: 'bug'>, <PokemonType.GHOST: 'ghost'>]
```

Puedes desactivar la hidratación por recurso:

```python
detailed = await client.get_pokemon_detailed(
    "mewtwo",
    hydrate_abilities=False,   # evita las consultas de habilidades
)
```

Los resultados hidratados se cachean **dos veces**: en memoria mientras vive
el cliente, y en disco vía `hishel`. Así que la segunda llamada para el
mismo Pokémon cuesta cero peticiones HTTP.

## Caché

Cada respuesta se cachea localmente en SQLite por defecto, en
`.cache/poke-wrap/cache.db`. Esto no es cortesía opcional — la política de
uso justo de PokeAPI pide explícitamente a los clientes que cacheen.
Configúralo así:

```python
client = AsyncPokeAPIClient(
    cache_ttl=3600,                       # 1 hora
    cache_path="/tmp/mi-cache-poke.db",   # ruta personalizada
)
```

`cache_ttl` se expresa en segundos. Las cabeceras de caché propias de
PokeAPI tienen prioridad cuando están presentes; `cache_ttl` es el respaldo.

## Manejo de errores

Todas las excepciones heredan de `PokeAPIError`:

```python
from poke_wrap import AsyncPokeAPIClient, ResourceNotFoundError, PokeAPIError

async with AsyncPokeAPIClient() as client:
    try:
        await client.get_pokemon("missingno")
    except ResourceNotFoundError as exc:
        print(f"{exc.resource_type}/{exc.resource_id} no encontrado")
    except PokeAPIError as exc:
        print(f"PokeWrap falló: {exc}")
```

Excepciones disponibles:

| Excepción | Cuándo |
|---|---|
| `PokeAPIError` | Clase base; captura cualquier error de PokeWrap. |
| `ResourceNotFoundError` | HTTP 404 de PokeAPI. |
| `RateLimitError` | HTTP 429 (incluye `retry_after` cuando está disponible). |
| `NetworkError` | Timeouts, fallos de DNS, conexiones rechazadas. |
| `HydrationError` | Una referencia durante la hidratación no pudo resolverse. |

## Requisitos

- Python 3.12 o superior.
- No se necesita autenticación para PokeAPI.

## Desarrollo

```bash
git clone https://github.com/Alike-Dev/poke-wrap
cd poke-wrap
uv sync
uv run pytest
```

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Licencia

MIT — ver [LICENSE](LICENSE).
