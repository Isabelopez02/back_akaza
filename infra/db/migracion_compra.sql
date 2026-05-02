-- ============================================================
-- MIGRACIÓN: Módulo de Compras
-- Ejecutar UNA sola vez en la base de datos existente.
-- ============================================================

-- 1. Columna para el precio anterior de compra en productos
ALTER TABLE productos
    ADD COLUMN IF NOT EXISTS precio_compra_anterior DECIMAL(10,2) NULL;

-- 2. Columna de unidad de medida en el historial de compras
--    (para saber si se compró en kg, litros o unidades en esa compra específica)
ALTER TABLE compras_historial
    ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(20) NULL;

-- Verificar
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('productos', 'compras_historial')
  AND column_name IN ('precio_compra_anterior', 'unidad_medida')
ORDER BY table_name, column_name;
