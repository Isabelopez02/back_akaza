-- LOMO SALTADO
INSERT INTO recetas (id_plato, id_producto, cantidad_estimada, unidad_medida) VALUES
(2, 4, 0.25, 'KG'), -- res
(2, 12, 0.10, 'KG'), -- cebolla
(2, 13, 0.10, 'KG'), -- tomate
(2, 1, 0.20, 'KG'), -- papa
(2, 2, 0.15, 'KG'); -- arroz

-- ARROZ CON POLLO
INSERT INTO recetas VALUES
(DEFAULT, 12, 3, 0.20, 'KG'),
(DEFAULT, 12, 2, 0.15, 'KG'),
(DEFAULT, 12, 16, 0.05, 'KG');

-- CEVICHE
INSERT INTO recetas VALUES
(DEFAULT, 15, 5, 0.25, 'KG'),
(DEFAULT, 15, 11, 0.15, 'KG'),
(DEFAULT, 15, 12, 0.05, 'KG'),
(DEFAULT, 15, 14, 0.03, 'KG');

-- AJI DE GALLINA
INSERT INTO recetas VALUES
(DEFAULT, 6, 14, 0.15, 'KG', FALSE), -- ají amarillo (base salsa)
(DEFAULT, 6, 3, 0.20, 'KG', FALSE),  -- pollo
(DEFAULT, 6, 17, 0.10, 'L', TRUE),   -- leche (puede ser light o evaporada)
(DEFAULT, 6, 8, 1, 'UNI', TRUE),     -- huevo (opcional)
(DEFAULT, 6, 18, 0.05, 'KG', TRUE);  -- queso fresco (opcional

-- BISTEC A LO POBRE
INSERT INTO recetas VALUES
(DEFAULT, 10, 4, 0.30, 'KG', FALSE), -- carne
(DEFAULT, 10, 1, 0.25, 'KG', TRUE),  -- papa
(DEFAULT, 10, 10, 1, 'UNI', TRUE),   -- plátano
(DEFAULT, 10, 9, 1, 'UNI', TRUE),    -- huevo
(DEFAULT, 10, 2, 0.10, 'KG', FALSE); -- arroz

--CHICARRON DE CALAMAR
INSERT INTO recetas VALUES
(DEFAULT, 24, 7, 0.30, 'KG', FALSE), -- calamar
(DEFAULT, 24, 1, 0.15, 'KG', TRUE),  -- papa opcional
(DEFAULT, 24, 11, 0.05, 'KG', TRUE); -- limón opcional

-- ==========================================================
-- SUSTITUCIONES PARA CHICHARRÓN DE CALAMAR (PLATO 24)
-- ==========================================================

-- 🦑 CALAMAR (ingrediente principal)
-- SOLO permitido si quieres variantes del plato
INSERT INTO sustituciones_permitidas (id_producto_original, id_producto_nuevo, costo_adicional) VALUES
(7, 5, 3.00),  -- calamar → pescado
(7, 6, 5.00);  -- calamar → mariscos mixtos

-- 🥔 PAPA (OPCIONAL en receta)
INSERT INTO sustituciones_permitidas VALUES
(DEFAULT, 1, 2, 0.50),  -- papa → arroz (guarnición alternativa)
(DEFAULT, 1, 20, 0.00);  -- papa → choclo (misma familia andina)

-- 🍋 LIMÓN (OPCIONAL / AJUSTE DE SABOR)
INSERT INTO sustituciones_permitidas VALUES
(DEFAULT, 11, 11, 0.00), -- mantener limón (sin cambio)
(DEFAULT, 11, 13, 0.00); -- limón → tomate (suavizar acidez)