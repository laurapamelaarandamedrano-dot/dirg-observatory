# Source registry

_Generated from `config/sources.yaml` and `data/raw/MANIFEST.csv` by `src/build_docs.py`._

Publicly accessible does not mean freely redistributable. `redistribution` states what this project publishes for each source: `raw_ok` (raw file could be redistributed, still fetched by script rather than committed), `derived_only` (only aggregates), `metadata_only` (citation and transformation notes only).

**Acquisition note for release 0.1.0.** The cloud environment that ran the pipeline could not reach `.gob.mx` hosts. Official files were therefore downloaded from the official URLs below in a desktop browser session on 2026-10-04 and their SHA-256 checksums recorded. `python -m src.ingest --fetch` downloads the same URLs directly; a checksum mismatch means the source changed upstream and must be logged in CHANGELOG.md.

## S01 · Monitor de Sequía de México: municipios con sequía (archivo histórico municipal)

- **Institution / author:** Servicio Meteorológico Nacional (SMN), Comisión Nacional del Agua (CONAGUA)
- **URL:** https://smn.conagua.gob.mx/es/climatologia/monitor-de-sequia/monitor-de-sequia-en-mexico
- **Publication date:** 2026-09-21
- **Access date:** 2026-10-04
- **License / terms:** Public government information (gob.mx). Specific terms not stated on the file; treated as derived_only pending confirmation.
- **Dataset type:** administrative
- **Geographic coverage:** Mexico, 2,4xx municipalities
- **Temporal coverage:** 2003-01 to 2026-09-15 (monthly, biweekly since 2014)
- **Redistribution:** `derived_only`
- **Methodological notes:** Categories D0 (abnormally dry) to D4 (exceptional drought). Blank cells mean no drought category assigned.
- **File:** `smn_MunicipiosSequia.xlsx` · 2,140,298 bytes · SHA-256 `87aa2b2e055e4ff91fc3ce32db2f3baefdf7ea23d51a0d32bacf73714885343a`

## S02 · Conciliación Demográfica 1950-2019 y Proyecciones de la Población de México y de las Entidades Federativas 2020-2070: indicadores demográficos

- **Institution / author:** Consejo Nacional de Población (CONAPO)
- **URL:** https://www.datos.gob.mx/dataset/proyecciones-de-poblacion
- **Publication date:** 2023
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** modelled
- **Geographic coverage:** National and 32 states
- **Temporal coverage:** 1950-2070 (1950-2019 conciliation; 2020-2070 projections)
- **Redistribution:** `raw_ok`
- **Methodological notes:** Values for 2020 onward are projections calibrated to the 2020 Census; they are coded as `modelled`.
- **File:** `conapo_indicadores.csv` · 1,689,266 bytes · SHA-256 `e0407d1640f38232023cf97656a0cb7be46049b1cb2344198c7e4aaec7cae6cd`

## S03 · Disponibilidad de agua subterránea (653 acuíferos), publicación 2023

- **Institution / author:** Comisión Nacional del Agua (CONAGUA)
- **URL:** https://www.datos.gob.mx/dataset/aguas_subterraneas
- **Publication date:** 2023
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** administrative
- **Geographic coverage:** 653 aquifers, each assigned to one state by CONAGUA (CLV_EDO)
- **Temporal coverage:** Single vintage (2023 publication; file stem dated 09-11-2023)
- **Redistribution:** `raw_ok`
- **Methodological notes:** Mean annual availability (DMA) computed under NOM-011-CONAGUA-2015. DMA_NEGATI < 0 means no availability (deficit).
- **File:** `conagua_disponibilidad.zip` · 4,111,514 bytes · SHA-256 `14afa0c98cd17392f19882e8890c731571932c87b301a70b8dcd2cb0a30b63f9`

## S04 · Ordenamientos de aguas subterráneas: vedas

- **Institution / author:** Comisión Nacional del Agua (CONAGUA)
- **URL:** https://www.datos.gob.mx/dataset/aguas_subterraneas
- **Publication date:** 2021-11-25
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** geospatial
- **Geographic coverage:** Polygons of groundwater vedas (prohibitions/restrictions) in force at file date
- **Temporal coverage:** Decrees with DOF dates; geometry as of 2021-11-25
- **Redistribution:** `raw_ok`
- **Methodological notes:** Descriptive regulatory layer. Not a legal assessment.
- **File:** `conagua_vedas.zip` · 3,418,397 bytes · SHA-256 `b67f1a0b79dc5fa9dbbf167fc268e20695492e1a9410aeb4d7c499a96af74c3f`

## S05 · Ordenamientos de aguas subterráneas: reglamentos y reservas de zonas reglamentadas

- **Institution / author:** Comisión Nacional del Agua (CONAGUA)
- **URL:** https://www.datos.gob.mx/dataset/aguas_subterraneas
- **Publication date:** 2023-01-13
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** geospatial
- **Geographic coverage:** 11 regulated zones
- **Temporal coverage:** As of 2023-01-13
- **Redistribution:** `raw_ok`
- **File:** `conagua_reglamentos.zip` · 26,905 bytes · SHA-256 `84cd1a80873ae744230c563bd03faa9de1d78a55edcfa86746492c357c7340ee`

## S06 · Ordenamientos de aguas subterráneas: acuerdo de suspensión provisional de libre alumbramiento

- **Institution / author:** Comisión Nacional del Agua (CONAGUA)
- **URL:** https://www.datos.gob.mx/dataset/aguas_subterraneas
- **Publication date:** 2021-11-25
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** geospatial
- **Geographic coverage:** Aquifers covered by suspension agreements
- **Temporal coverage:** As of 2021-11-25
- **Redistribution:** `raw_ok`
- **File:** `conagua_suspension.zip` · 2,041,149 bytes · SHA-256 `5f00f7370b302b05ccc9ecfaca1289fefe1f65a18e5deef15d9983a58e19e14e`

## S07 · Lista de permisos otorgados de generación de energía eléctrica: histórico (1963 - febrero de 2026)

- **Institution / author:** Comisión Nacional de Energía (CNE)
- **URL:** https://www.datos.gob.mx/dataset/electricidad
- **Publication date:** 2026-04-20
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** administrative
- **Geographic coverage:** Permits by state and municipality
- **Temporal coverage:** 1963 to 2026-02
- **Redistribution:** `derived_only`
- **Methodological notes:** Raw file names permit holders and lists street addresses with coordinates. The observatory publishes ONLY state-year aggregates of authorized capacity; holder names, addresses and coordinates are dropped at ingestion (see DATA_GOVERNANCE_AUDIT.md). Authorized capacity is not equal to installed or dispatched capacity.
- **File:** `cne_permisos_gen_hist.csv` · 816,993 bytes · SHA-256 `afafac19916688a3901959feb168c470780a36ff13833e93df1cd3d0352a7e98`

## S08 · Índice de marginación por entidad federativa 2020

- **Institution / author:** Consejo Nacional de Población (CONAPO)
- **URL:** https://www.datos.gob.mx/dataset/indices_marginacion
- **Publication date:** 2021
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** derived
- **Geographic coverage:** 32 states
- **Temporal coverage:** 2020 (Census 2020 based)
- **Redistribution:** `raw_ok`
- **Methodological notes:** IMN_2020 is CONAPO's normalized marginalization index (0-1 scale, higher = more marginalized).
- **File:** `conapo_ime_2020.csv` · 7,793 bytes · SHA-256 `d23d1fd1847f2ca0d3171c480fe53ae3f15d182efcb70085ae54576d5c84a4bb`

## S09 · Vulnerabilidad social, económica y ambiental a la sequía por municipio

- **Institution / author:** Comisión Nacional del Agua (CONAGUA), Programa Nacional Contra la Sequía (PRONACOSE)
- **URL:** https://www.datos.gob.mx/dataset/programa_nacional_contra_sequia_pronacose
- **Publication date:** undated
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** modelled
- **Geographic coverage:** Municipalities
- **Temporal coverage:** Undated vintage; treated as time-invariant with a recency penalty
- **Redistribution:** `raw_ok`
- **Methodological notes:** Probabilities (0-100) estimated by CONAGUA from indicator sets. The vintage year is not stated in the published resource; the observatory flags this as UNDATED_VINTAGE.
- **File:** `pronacose_vuln_social.csv` · 99,425 bytes · SHA-256 `134d4dd69bcb7c3873965650b2574fde8ae42fd123906c3b847ad93199ed4a58`
- **File:** `pronacose_vuln_economica.csv` · 87,013 bytes · SHA-256 `cf4cbbe91cb4fb00c7194cbf507d18335f4d8f3e9072515b826b7126374d51d0`
- **File:** `pronacose_vuln_ambiental.csv` · 86,960 bytes · SHA-256 `f4bf312897f3831889e10fd5c48ed6e3753b0467eef6e149b7060b776af3f4b0`

## S10 · Instrumentos de Política Climática en México por Entidad Federativa (1975-2025)

- **Institution / author:** Instituto Nacional de Ecología y Cambio Climático (INECC)
- **URL:** https://www.datos.gob.mx/dataset/instrumentos_politica_climatica_mexico_entidad_federativa
- **Publication date:** 2025
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** documentary
- **Geographic coverage:** 32 states
- **Temporal coverage:** Instruments published 1975-2025
- **Redistribution:** `raw_ok`
- **Methodological notes:** Governance layer only. Counts of instruments are descriptive and say nothing about their effectiveness.
- **File:** `inecc_instrumentos.csv` · 97,622 bytes · SHA-256 `351820a2539aa28d23c56b4db17b0702b2796ece6865c57aa042071a508f8201`

## S11 · Consumo final de energía eléctrica (2016 a 2025)

- **Institution / author:** Comisión Federal de Electricidad (CFE)
- **URL:** https://www.datos.gob.mx/dataset/consumo_final_energia_electrica
- **Publication date:** 2026-03-13
- **Access date:** 2026-10-04
- **License / terms:** CC BY 4.0 (datos.gob.mx)
- **Dataset type:** administrative
- **Geographic coverage:** National only
- **Temporal coverage:** 2016-01 to 2025-12, monthly
- **Redistribution:** `raw_ok`
- **Methodological notes:** National context series. NOT territorial: it cannot enter the state-level index.
- **File:** `cfe_consumo_final.csv` · 2,779 bytes · SHA-256 `53251e23c7ba101c1d0ca5e791402e6094204f82c961849d34e42091c7f9758d`

## S12 · Admin 1 – States, Provinces (1:10m), v5

- **Institution / author:** Natural Earth
- **URL:** https://www.naturalearthdata.com/
- **Publication date:** 2022
- **Access date:** 2026-10-04
- **License / terms:** Public domain
- **Dataset type:** geospatial
- **Geographic coverage:** World; filtered to the 32 Mexican states
- **Temporal coverage:** Static
- **Redistribution:** `raw_ok`
- **Methodological notes:** Used for display geometry and state areas. Official analytical boundaries are INEGI's Marco Geoestadístico; NE boundaries are generalized. Areas computed from NE are approximate (see METHODOLOGY).
- **File:** `ne_10m_admin1_mexico.geojson` · 589,975 bytes · SHA-256 `bdbcc8befca9ba3371b7e1d200399b2e49e0d79fc0c689f0d857d97d2d87552a`

## S13 · land-110m.json v2.0.2

- **Institution / author:** world-atlas (M. Bostock), derived from Natural Earth
- **URL:** https://github.com/topojson/world-atlas
- **Publication date:** 2020
- **Access date:** 2026-10-04
- **License / terms:** ISC (data: Natural Earth, public domain)
- **Dataset type:** geospatial
- **Geographic coverage:** World land
- **Temporal coverage:** Static
- **Redistribution:** `raw_ok`
- **Methodological notes:** Globe basemap only.
- **File:** `world_land_110m.topo.json` · 55,207 bytes · SHA-256 `ead5f68119c49a9250902e7da303bcb209341bbb8fefe7369a439b48b704658a`

## S20 · Release note: New region in Queretaro, Mexico (mx-queretaro-1)

- **Institution / author:** Oracle Cloud Infrastructure documentation
- **URL:** https://docs.oracle.com/en-us/iaas/releasenotes/changes/75aca8c4-b80f-4892-bc5c-b6748ec4b5d7/index.htm
- **Publication date:** 2022-07-15
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro
- **Temporal coverage:** 2022
- **Redistribution:** `metadata_only`
- **Methodological notes:** Primary (provider) source.

## S21 · Release note: New region in Monterrey, Mexico (mx-monterrey-1)

- **Institution / author:** Oracle Cloud Infrastructure documentation
- **URL:** https://docs.oracle.com/en-us/iaas/releasenotes/changes/b2b79dfd-1a85-4a96-841a-6686b8e0f78f/
- **Publication date:** 2023-07-13
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Nuevo León
- **Temporal coverage:** 2023
- **Redistribution:** `metadata_only`
- **Methodological notes:** Primary (provider) source.

## S22 · Microsoft Launches First Cloud Data Center in Mexico

- **Institution / author:** Mexico Business News
- **URL:** https://mexicobusiness.news/cloudanddata/news/microsoft-launches-first-cloud-data-center-mexico
- **Publication date:** 2024-05-08
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro metropolitan area
- **Temporal coverage:** 2024
- **Redistribution:** `metadata_only`
- **Methodological notes:** Secondary source (press).

## S23 · Google launches Mexican cloud region in Querétaro

- **Institution / author:** DatacenterDynamics
- **URL:** https://www.datacenterdynamics.com/en/news/google-launches-mexican-cloud-region-in-queretaro/
- **Publication date:** 2024-12-07
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro
- **Temporal coverage:** 2024
- **Redistribution:** `metadata_only`
- **Methodological notes:** Secondary source (trade press).

## S24 · Now open – AWS Mexico (Central) Region (mx-central-1)

- **Institution / author:** Amazon Web Services News Blog
- **URL:** https://aws.amazon.com/blogs/aws/now-open-aws-mexico-central-region
- **Publication date:** 2025-01-14
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Mexico (Central)
- **Temporal coverage:** 2025
- **Redistribution:** `metadata_only`
- **Methodological notes:** Primary source does not name the state. State attribution (Querétaro) relies on S25.

## S25 · AWS to launch an infrastructure region in Mexico

- **Institution / author:** Amazon (press release)
- **URL:** https://press.aboutamazon.com/2024/2/aws-to-launch-an-infrastructure-region-in-mexico
- **Publication date:** 2024-02-25
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro
- **Temporal coverage:** 2024
- **Redistribution:** `metadata_only`
- **Methodological notes:** Location attribution for S24; confidence recorded as `secondary` in the register.

## S26 · Alibaba Cloud launches Mexico cloud region

- **Institution / author:** DatacenterDynamics
- **URL:** https://www.datacenterdynamics.com/en/news/alibaba-cloud-launches-mexico-cloud-region/
- **Publication date:** 2025-02-19
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro
- **Temporal coverage:** 2025
- **Redistribution:** `metadata_only`
- **Methodological notes:** Secondary source (trade press).

## S27 · Huawei cloud data centres in Estado de México (first opened 2019; second region 2021)

- **Institution / author:** Xataka México; Mexico Business News
- **URL:** https://www.xataka.com.mx/telecomunicaciones/huawei-no-solo-smartphones-empresa-apuesta-mexico-nube-abrira-su-segundo-centro-datos-tultitlan-edomex (secondary: https://mexicobusiness.news/tech/news/huawei-opens-second-cloud-region)
- **Publication date:** 2021-10-26
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Estado de México
- **Temporal coverage:** 2019-2021
- **Redistribution:** `metadata_only`
- **Methodological notes:** Secondary sources; opening years are reported at year precision only.

## S28 · El boom de data centers en Querétaro; acapara el 79% nacional

- **Institution / author:** DatacenterDynamics (Spanish edition)
- **URL:** https://www.datacenterdynamics.com/es/noticias/el-boom-de-data-centers-en-quer%C3%A9taro-acapara-el-79-nacional/
- **Publication date:** 2026-02-12
- **Access date:** 2026-10-04
- **License / terms:** Copyrighted web page; facts cited, text not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Querétaro
- **Temporal coverage:** May 2025
- **Redistribution:** `metadata_only`
- **Methodological notes:** Reports 186 MW operating in Querétaro as of May 2025 (~79% of national). The article does not attribute the figure to a named primary source; kept as CONTEXT ONLY, never in the index.

## S40 · Constitución Política de los Estados Unidos Mexicanos (texto vigente)

- **Institution / author:** Cámara de Diputados del H. Congreso de la Unión
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf
- **Publication date:** 1917-02-05 (last reform varies)
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`

## S41 · Ley General de Aguas and reform decree of the Ley de Aguas Nacionales

- **Institution / author:** Diario Oficial de la Federación; Holland & Knight (summary)
- **URL:** https://www.hklaw.com/es/insights/publications/2025/12/mexico-aprueba-la-nueva-ley-general-de-aguas-y-reformas (secondary: https://www.supremacorte.gob.mx/sites/default/files/sintesis_dof_gocdmx/documento/2026-01/DOF%2011122025%20S%C3%8DNTESIS.pdf)
- **Publication date:** 2025-12-11
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public); law-firm summary cited, not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** From 2025-12
- **Redistribution:** `metadata_only`
- **Methodological notes:** DOF date taken from the SCJN DOF synthesis of 2025-12-11. Requires verification against the DOF edition before formal legal citation.

## S42 · Ley del Sector Eléctrico; Ley de la Comisión Nacional de Energía; Ley de Planeación y Transición Energética (DOF 2025-03-18)

- **Institution / author:** Diario Oficial de la Federación; White & Case (summary)
- **URL:** https://whitecase.com/sites/default/files/2025-03/nuevas-leyes-en-materia-de-energia-esp.pdf
- **Publication date:** 2025-03-18
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public); law-firm summary cited, not reproduced
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** From 2025-03
- **Redistribution:** `metadata_only`
- **Methodological notes:** Abrogated Ley de la Industria Eléctrica and Ley de Transición Energética; CNE replaced CRE.

## S43 · Ley en Materia de Telecomunicaciones y Radiodifusión (DOF 2025-07-16)

- **Institution / author:** Diario Oficial de la Federación; IDC Online (summary)
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LMTR.pdf (secondary: https://idconline.mx/corporativo/2025/07/24/nueva-ley-de-telecomunicaciones-y-radiodifusion-claves)
- **Publication date:** 2025-07-16
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** From 2025-07
- **Redistribution:** `metadata_only`
- **Methodological notes:** Creates the Comisión Reguladora de Telecomunicaciones attached to the Agencia de Transformación Digital y Telecomunicaciones.

## S44 · Ley General del Equilibrio Ecológico y la Protección al Ambiente

- **Institution / author:** Cámara de Diputados
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGEEPA.pdf
- **Publication date:** 1988-01-28 (texto vigente)
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`

## S45 · Ley General de Asentamientos Humanos, Ordenamiento Territorial y Desarrollo Urbano

- **Institution / author:** Cámara de Diputados
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGAHOTDU.pdf
- **Publication date:** 2016-11-28 (texto vigente)
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`

## S46 · NOM-011-CONAGUA-2015, Conservación del recurso agua: especificaciones y método para determinar la disponibilidad media anual de las aguas nacionales

- **Institution / author:** CONAGUA / DOF
- **URL:** https://www.dof.gob.mx/nota_detalle.php?codigo=5387027&fecha=27/03/2015
- **Publication date:** 2015-03-27
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`
- **Methodological notes:** Defines the method behind S03.

## S47 · Ley General de Cambio Climático

- **Institution / author:** Cámara de Diputados
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGCC.pdf
- **Publication date:** 2012-06-06 (texto vigente)
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`

## S48 · Ley Federal de Derechos (zonas de disponibilidad para cuotas de agua)

- **Institution / author:** Cámara de Diputados
- **URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf
- **Publication date:** 1981-12-31 (texto vigente)
- **Access date:** 2026-10-04
- **License / terms:** Official legal text (public)
- **Dataset type:** documentary
- **Geographic coverage:** Federal
- **Temporal coverage:** In force
- **Redistribution:** `metadata_only`

