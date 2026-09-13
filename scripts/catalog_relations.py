"""Resolve reviewed catalog relationships without inheriting admission or fee rules."""


def attach_relations(programs):
    lookup = {}
    for program in programs:
        identity = program.get('inventory_identity', program)
        for key in {program['id'], identity['id']}:
            assert key not in lookup or lookup[key] is program, f'Ambiguous program identity: {key}'
            lookup[key] = program
        program['related_parents'] = []
        program['related_children'] = []
    for program in programs:
        identity = program.get('inventory_identity', program)
        parents = identity.get('parent_program_ids')
        if parents is None:
            parent = identity.get('parent_program_id') or identity.get('parent_inventory_id')
            parents = [parent] if parent else []
        assert isinstance(parents, list) and len(parents) == len(set(parents)), program['id']
        resolved_parents = set()
        for parent_id in parents:
            assert parent_id in lookup, f'Unknown parent: {parent_id}'
            parent = lookup[parent_id]
            assert parent['university_id'] == program['university_id'], f'Cross-school parent: {parent_id}'
            assert parent is not program, f'Self parent: {parent_id}'
            assert parent['id'] not in resolved_parents, f'Duplicate resolved parent: {parent_id}'
            resolved_parents.add(parent['id'])
            program['related_parents'].append({'id': parent['id'], 'name': parent['name']})
            parent['related_children'].append({'id': program['id'], 'name': program['name']})
    active, done = set(), set()

    def visit(program):
        pid = program['id']
        assert pid not in active, f'Cyclic program relationship: {pid}'
        if pid in done:
            return
        active.add(pid)
        for parent in program['related_parents']:
            visit(lookup[parent['id']])
        active.remove(pid)
        done.add(pid)

    for program in programs:
        visit(program)
