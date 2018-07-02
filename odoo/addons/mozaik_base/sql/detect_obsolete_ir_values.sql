select * from ir_values k
where value like 'ir.actions.act_window,%'
and 0 = (select count(*) from ir_act_window where id = replace(k.value,'ir.actions.act_window,','')::integer)
union
select * from ir_values k
where value like 'ir.actions.act_url,%'
and 0 = (select count(*) from ir_act_url where id = replace(k.value,'ir.actions.act_url,','')::integer)
union
select * from ir_values k
where value like 'ir.actions.act_server,%'
and 0 = (select count(*) from ir_act_server where id = replace(k.value,'ir.actions.act_server,','')::integer)
union
select * from ir_values k
where value like 'ir.actions.act_client,%'
and 0 = (select count(*) from ir_act_client where id = replace(k.value,'ir.actions.act_client,','')::integer)
