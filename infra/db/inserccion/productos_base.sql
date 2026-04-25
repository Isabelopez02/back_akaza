-- ==========================================
-- PRODUCTOS BASE (INGREDIENTES)
-- Estos IDs deben coincidir con los que usa 2.sql
-- ==========================================

INSERT INTO productos (id, nombre, unidad_medida, stock_actual, stock_minimo_alerta) VALUES
(1, 'Papa', 'KG', 50.00, 5.00),
(2, 'Arroz', 'KG', 30.00, 3.00),
(3, 'Pollo', 'KG', 20.00, 2.00),
(4, 'Res', 'KG', 15.00, 2.00),
(5, 'Pescado blanco', 'KG', 10.00, 1.00),
(6, 'Mariscos mixtos', 'KG', 8.00, 1.00),
(7, 'Calamar', 'KG', 5.00, 1.00),
(8, 'Huevo', 'UNI', 100.00, 10.00),
(9, 'Huevo frito', 'UNI', 50.00, 5.00),
(10, 'Plátano', 'UNI', 30.00, 3.00),
(11, 'Limón', 'KG', 10.00, 1.00),
(12, 'Cebolla', 'KG', 20.00, 2.00),
(13, 'Tomate', 'KG', 15.00, 2.00),
(14, 'Ají amarillo', 'KG', 5.00, 0.50),
(15, 'Pescado fresco', 'KG', 12.00, 1.00),
(16, 'Culantro', 'KG', 3.00, 0.30),
(17, 'Leche', 'L', 10.00, 1.00),
(18, 'Queso fresco', 'KG', 5.00, 0.50),
(20, 'Choclo', 'KG', 10.00, 1.00)

ON CONFLICT (id) DO NOTHING;
