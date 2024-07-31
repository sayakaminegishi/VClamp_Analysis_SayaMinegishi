%test script - shows an example usage of my find_synaptic_charge_single()
%function.

% Created by Sayaka (Saya) Minegishi
% 3/23/24

filename = "2016_05_19_07_0002 (1).abf";
filenameExcelExport = "excel_vclamp1.xlsx"
synaptic_charge_table = find_synaptic_charge_single(filename,filenameExcelExport)

%INTEGRATE PYTHON
res = py.list({"Name1","Name2","Name3"})

mylist = string(res) %To convert the list variable to a MATLAB variable, call string.
%Call the search function. Type py. in front of the module name and function name.
N = py.list({'Jones','Johnson','James'})
names = py.mymod.search(N)