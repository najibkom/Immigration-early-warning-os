# Signal taxonomy (v0.2: six categories)

Confirm with the client; add codes, never reuse one for another meaning. The prefix gives the scoring category.

## ECO — Economy, incl. employment and SMEs → `econ`
- ECO-JOB — unemployment, youth unemployment
- ECO-SME — SME closures, layoffs, sector shocks
- ECO-FOOD — staple food prices
- ECO-FX — currency depreciation, inflation
- ECO-REM — remittance flows
- ECO-SHOCK — sudden shock (plant closure, harvest-linked income loss, trade halt)

## ENV — Weather and environment → `env`
- ENV-DRT — drought index / rainfall deficit
- ENV-FLD — flood
- ENV-HEAT — extreme heat
- ENV-CROP — crop failure / livestock loss
- ENV-WAT — water scarcity

## POL — Politics and security, incl. protests and conflict → `politics`
- POL-VISA — visa rule change
- POL-BRD — border opening/closure, controls
- POL-ASY — asylum procedure change
- POL-LAB — labour migration programme change
- POL-PRO — protests, strikes, unrest (event counts)
- POL-CONF — armed conflict, violence events (counts, region level)
- POL-CONTRA — contradictory official texts (forces human hold)

## SOC — Social and health, incl. disease → `social`
- SOC-DIS — disease outbreak, epidemic
- SOC-SERV — health/education service disruption
- SOC-FOOD — food insecurity (IPC phase)
- SOC-DISP — internal displacement already observed

## MED — Social media trends (aggregate only) → `media`
- MED-VOL — topic volume velocity
- MED-SRCH — search frequency (routes, visas, jobs abroad)
- MED-SENT — sentiment shift (shares)
- MED-NOISE — viral chatter unrelated to migration (used to dampen)

## OTH — Other → `other`
- OTH-xxx — define the code when first used, with a one-line meaning

## OUT — Outcomes (not scored; what the system learns to anticipate)
- OUT-ARR — arrivals at destination
- OUT-CROSS — irregular crossings / interceptions
- OUT-ASY — asylum applications
- OUT-INT — departure intentions (survey)
