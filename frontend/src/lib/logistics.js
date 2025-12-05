// Frontend implementation of backend logistics calculations
export function roundToMeaningful(value, decimalPlaces = 1) {
  if (value === Math.trunc(value)) return Math.trunc(value);

  const integerPart = Math.trunc(value);
  const decimalPart = value - integerPart;

  if (decimalPart >= 0.1 && decimalPart <= 0.5) return integerPart + 0.5;
  if (decimalPart >= 0.6 && decimalPart <= 0.9) return integerPart + 1;
  return Number(value.toFixed(decimalPlaces));
}

export function recommendTransport(quantity_sacks) {
  if (quantity_sacks > 10) return 'lorry';
  if (quantity_sacks > 3) return 'pickup';
  return 'motorbike';
}

export function computeTransportCost(quantity_sacks, mode) {
  const rates = { motorbike: 1000, pickup: 700, lorry: 400 };
  const rate = rates[mode];
  return rate * quantity_sacks;
}

export function kgToSacks(quantity_kg, kg_per_sack = 90) {
  return quantity_kg / kg_per_sack;
}

export function computeTransportCostDetailed(quantity_kg, distance_km, kg_per_sack = 90) {
  const quantity_sacks = kgToSacks(quantity_kg, kg_per_sack);
  const quantity_sacks_rounded = roundToMeaningful(quantity_sacks);
  const mode = recommendTransport(quantity_sacks_rounded >= 1 ? Math.trunc(quantity_sacks_rounded) : 1);

  const ratesPerSack = { motorbike: 1000, pickup: 700, lorry: 400 };
  const costPerSack = ratesPerSack[mode];
  const costPerKm = 10;
  const distanceKmRounded = roundToMeaningful(distance_km);

  const baseCost = costPerSack * quantity_sacks_rounded;
  const distanceCost = distanceKmRounded * costPerKm;
  const totalCost = baseCost + distanceCost;

  return {
    quantity_sacks: quantity_sacks_rounded,
    transport_mode: mode,
    cost_per_sack: costPerSack,
    cost_per_km: costPerKm,
    distance_km: distanceKmRounded,
    base_cost: Math.round(baseCost),
    distance_cost: Math.round(distanceCost),
    total_cost: Math.round(totalCost),
  };
}

export function buildLogisticsPlan(quantity_sacks, distance_km, best_market_location, market_price) {
  const mode = recommendTransport(quantity_sacks);
  const cost = computeTransportCost(quantity_sacks, mode);
  return {
    transport_mode: mode,
    transport_cost_kes: cost,
    distance_km,
    best_market_location,
    market_price,
  };
}
