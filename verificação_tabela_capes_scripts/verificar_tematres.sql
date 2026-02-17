-- 1. Contagem Total de Termos
-- Este comando confirma quantos temas foram importados no total.

--SQL
SELECT COUNT(*) AS total_termos 
FROM lc_tema;

-- 2. Contagem de Grandes Áreas (Termos Raiz)
-- No seu banco de dados, os termos raiz são aqueles que não possuem um pai na tabela lc_tabla_rel com o tipo de relação hierárquica (geralmente t_relacion = 3 para relações Broader/Narrower no Tematres).

--SQL
SELECT COUNT(*) AS total_grandes_areas 
FROM lc_tema t
WHERE NOT EXISTS (
    SELECT 1 
    FROM lc_tabla_rel r 
    WHERE r.id_menor = t.tema_id 
    AND r.t_relacion = 3
);
-- 3. Listar as Grandes Áreas e seus IDs
-- Útil para verificar se áreas como "Ciências Exatas e da Terra" (ID 1) ou "Ciências Biológicas" (ID 246) estão corretamente configuradas como topo da hierarquia.

--SQL
SELECT tema_id, tema, cuando
FROM lc_tema t
WHERE NOT EXISTS (
    SELECT 1 
    FROM lc_tabla_rel r 
    WHERE r.id_menor = t.tema_id 
    AND r.t_relacion = 3
)
ORDER BY tema ASC;
-- 4. Verificar se existem Termos Orfãos
-- Um termo orfão é aquele que não é Raiz (deveria ter um pai), mas a relação não existe ou está quebrada. Como seu banco usa a tabela lc_indice para caminhos, podemos cruzar esses dados.

--SQL
-- Verifica termos que não são raiz mas não possuem relação de pai definida
SELECT tema_id, tema 
FROM lc_tema t
WHERE tema_id NOT IN (
    -- Termos que são filhos de alguém
    SELECT id_menor FROM lc_tabla_rel WHERE t_relacion = 3
)
AND tema_id NOT IN (
    -- Liste aqui IDs que você sabe que são Raiz (ex: 1, 246, 370...)
    1, 246, 370, 666, 747, 904, 1092, 1266, 1319
);
-- 5. Validar a Integridade da Tabela de Índices
-- O Tematres usa a tabela lc_indice para buscas rápidas de hierarquia (ex: |1|2|10). Este comando mostra se há divergência entre a contagem de temas e a de índices.

--SQL
SELECT 
    (SELECT COUNT(*) FROM lc_tema) AS qtd_temas,
    (SELECT COUNT(*) FROM lc_indice) AS qtd_indices;