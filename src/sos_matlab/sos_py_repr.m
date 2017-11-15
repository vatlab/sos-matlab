% This file is part of Script of Scripts (sos), a workflow system
% for the execution of commands and scripts in different languages.
% Please visit https://github.com/vatlab/SOS for more information.
%
% Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program. If not, see <http://www.gnu.org/licenses/>.

function [repr] = sos_py_repr (obj)
% isnumeric(A) returns true if A is a numeric array and false otherwise.
% single Single-precision floating-point array
% double Double-precision floating-point array
% int8 8-bit signed integer array
% uint8 8-bit unsigned integer array
% int16 16-bit signed integer array
% uint16 16-bit unsigned integer array
% int32 32-bit signed integer array
% uint32 32-bit unsigned integer array
% int64 64-bit signed integer array
% uint64 64-bit unsigned integer array
if isnumeric(obj)
    % isscalar(A) returns logical 1 (true) if size(A) returns [1 1], and logical 0 (false) otherwise.
    if isscalar(obj)
        if isinf(obj)
            if obj > 0
                repr = 'np.inf';
            else
                repr = '-np.inf';
            end
        % complex
        elseif isreal(obj) == 0
            rl = num2str(real(obj));
            im = num2str(imag(obj));
            repr = strcat('complex(', rl, ',', im, ')');
        % none
        elseif isnan(obj)
            repr = 'None';
        else
            repr = num2str(obj);
        end
    % isvector(A) returns logical 1 (true) if size(A) returns [1 n] or [n 1] with a nonnegative integer value n, and logical 0 (false) otherwise.
    elseif isvector(obj)
        if any(isinf(obj))
            repr = strcat('np.array([', strjoin(arrayfun(@(x) sos_py_repr(x), obj, 'UniformOutput', false),','), '])');
        elseif any(isnan(obj))
            repr = strcat('np.array([', strjoin(arrayfun(@(x) sos_py_repr(x), obj, 'UniformOutput', false),','), '])');
        else
            repr = strcat('np.array([', strjoin(arrayfun(@(x) num2str(x), obj, 'UniformOutput',false),','), '])');
        end
    % ismatrix(V) returns logical 1 (true) if size(V) returns [m n] with nonnegative integer values m and n, and logical 0 (false) otherwise.
    elseif ismatrix(obj)
        save('-v6', fullfile(tempdir, 'mat2py.mat'), 'obj');
        repr = strcat('np.matrix(sio.loadmat(''', tempdir, 'mat2py.mat'')', '[''', 'obj', '''])');
    % other, maybe canbe improved with the vector's block
    else
        % not sure what this could be
        repr = num2str(obj);
    end
% char_arr_var
elseif ischar(obj) && length(obj)>1 && size(obj,2)==1
    repr = '[';
    for i = 1:length(obj)
        repr = strcat(repr, sos_py_repr(obj(i,1)), ',');
    end
    repr = strcat(repr,']');
% string
elseif ischar(obj)
    repr =strcat('r"""',obj,'"""');
% structure
elseif isstruct(obj)
    fields = fieldnames(obj);
    repr = '{';
    for i = 1:numel(fields)
        repr = strcat(repr, '"', fields{i}, '":', sos_py_repr(obj.(fields{i})), ',');
    end
    repr = strcat(repr, '}');
    
    %save('-v6', fullfile(tempdir, 'stru2py.mat'), 'obj');
    %repr = strcat('sio.loadmat(''', tempdir, 'stru2py.mat'')', '[''', 'obj', ''']');
% cell
elseif iscell(obj)
    if size(obj,1)==1
        repr = '[';
        for i = 1:size(obj,2)
            repr = strcat(repr, sos_py_repr(obj{1,i}), ',');
        end
        repr = strcat(repr,']');
    else
        save('-v6', fullfile(tempdir, 'cell2py.mat'), 'obj');
        repr = strcat('sio.loadmat(''', tempdir, 'cell2py.mat'')', '[''', 'obj', ''']');
    end
% boolean
elseif islogical(obj)
    if length(obj)==1
        if obj
            repr = 'True';
        else
            repr = 'False';
        end
    else 
        repr = '[';
        for i = 1:length(obj)
            repr = strcat(repr, sos_py_repr(obj(i)), ',');
        end
        repr = strcat(repr,']');
    end
            
% table, table usually is also real, and can be a vector and matrix
% sometimes, so it needs to be put in front of them.
elseif istable(obj)
    cd (tempdir);
    writetable(obj,'tab2py.csv','Delimiter',',','QuoteStrings',true);
    repr = strcat('pd.read_csv(''', tempdir, 'tab2py.csv''', ')');
    else
        % unrecognized/unsupported datatype is transferred from
        % matlab to Python as string "Unsupported datatype"
        repr = 'Unsupported datatype';
    end
end
