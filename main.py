from abc_py.classes import ABC

abc = ABC()
abc.read_aiger("i10.aig")
print(abc.print_stats())
abc.balance()
print(abc.print_stats())
abc.balance()
abc.rewrite(preserve_levels=False)
abc.rewrite(preserve_levels=False, zero_cost=True)
abc.balance()
abc.rewrite(preserve_levels=False, zero_cost=True)
abc.balance()
print(abc.print_stats())
# abc.cec()
abc.quit()
