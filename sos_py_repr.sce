function [repr] = sos_py_repr (obj)
/*isnumeric(A) returns true if A is a numeric array and false otherwise.
% single Single-precision floating-point array
% double Double-precision floating-point array
% int8 8-bit signed integer array
% uint8 8-bit unsigned integer array
% int16 16-bit signed integer array
% uint16 16-bit unsigned integer array
% int32 32-bit signed integer array
% uint32 32-bit unsigned integer array
% int64 64-bit signed integer array
% uint64 64-bit unsigned integer array */
if type(obj) == 1
    // isscalar(A) returns logical 1 (true) if size(A) returns [1 1], and logical 0 (false) otherwise.
    //done
    if size(obj) == [1,1]
        if isinf(obj)
            if obj > 0
                repr = 'np.inf';
            else
                repr = '-np.inf';
            end
        // complex
        elseif isreal(obj) == %f
            rl = string(real(obj));
            im = string(imag(obj));
            repr = strcat(['complex(', rl, ',', im, ')']);
        // none
        elseif isnan(obj)
            repr = 'None';
        else
            repr = string(obj);
        end
    // % isvector(A) returns logical 1 (true) if size(A) returns [1 n] or [n 1] with a nonnegative integer value n, and logical 0 (false) otherwise.
    // DONE!!
    elseif size(obj, 'r')==1 | size(obj, 'c')==1
            if or(isinf(obj))
                repr = strcat(['np.array([', arrfun(obj, sos_py_repr), '])']);
            elseif or(isnan(obj))
                repr = strcat(['np.array([', arrfun(obj, sos_py_repr), '])']);
            elseif and(isreal(obj))
                repr = strcat(['np.array([', arrfun(obj, string), '])']);
            else
                repr = strcat(['np.array([', arrfun(obj, sos_py_repr), '])']);
            end
    // ismatrix(V) returns logical 1 (true) if size(V) returns [m n] with nonnegative integer values m and n, and logical 0 (false) otherwise.
    // DONE!
    elseif size(obj, 'r')>1 && size(obj, 'c')>1
        savematfile( TMPDIR + '/mat2py.mat', 'obj', '-v6');
        repr = strcat(['np.matrix(sio.loadmat(r''', TMPDIR, 'mat2py.mat'')', '[''', 'obj', '''])']);
        // outputs: "np.matrix(sio.loadmat(r'/tmp/SCI_TMP_1607379_Bv9sEVmat2py.mat')['obj'])"
        // ^ is this correct?
    elseif length(size(obj)) >= 3
        //% 3d or even higher matrix
        savematfile( TMPDIR + '/mat2py.mat', 'obj', '-v6');
        repr = strcat(['sio.loadmat(r''', TMPDIR, 'mat2py.mat'')', '[''', 'obj', ''']']);
    // % other, maybe canbe improved with the vector's block
    else
        // % not sure what this could be
        repr = string(obj);
    end

    
// % char_arr_var
elseif ischar(obj) && size(obj, 1) > 1
    repr = '[';
    for i = 1:size(obj, 1)
        repr = strcat([repr, 'r"""', (obj(i, :)), '""",']);
    end
    repr = strcat([repr,']']);


// % string
// done
elseif ischar(obj)
    repr =strcat(['r""',obj,'""']);
// % structure
// done
elseif isstruct(obj)
    fields = fieldnames(obj);
    repr = '{';
    for i=fields
        repr = strcat([repr, '""', i, '"":', sos_py_repr(obj(i)), ',']);
    end
    repr = strcat([repr, '}']);

    // %save('-v6', fullfile(tempdir, 'stru2py.mat'), 'obj');
    // %repr = strcat('sio.loadmat(r''', tempdir, 'stru2py.mat'')', '[''', 'obj', ''']');

// % cell
//done
elseif iscell(obj)
    if size(obj,1)==1
        repr = '[';
        for i = 1:length(obj)
            repr = strcat([repr, sos_py_repr(obj{i}), ','])
        end
        //done
        repr = strcat([repr,']']);
    else
        //done
        savematfile( TMPDIR + '/cell2py.mat', 'obj', '-v6');
        repr = strcat(['sio.loadmat(r''', TMPDIR, 'cell2py.mat'')', '[''', 'obj', ''']']);
    end
// % boolean
//done
elseif type(obj)==4
    if length(obj)==1
        if obj
            repr = 'True';
        else
            repr = 'False';
        end
        // else
        // repr = '[';
        // for i = 1:length(obj)
        //     repr = strcat([repr, sos_py_repr(obj(i)), ',']);
        // end
        // repr = strcat([repr,']']); 
    end

// % table, table usually is also real, and can be a vector and matrix sometimes, so it needs to be put in front of them.
//DONE!
elseif istable(obj)
    cd (TMPDIR);
    csvWrite(obj,'tab2py.csv',',','QuoteStrings',true);
    repr = strcat(['pd.read_csv(''', TMPDIR, 'tab2py.csv''', ')']);
    else
        // % unrecognized/unsupported datatype is transferred from
        // % matlab to Python as string "Unsupported datatype"
        repr = 'Unsupported datatype';
    end
endfunction


//replace arrayfun
function[newstr] = arrfun(obj, func)
new=[]
for i=obj
    new($+1) = func(i);
    new($+1) = ','
end
new($) = ''
newstr = strcat(new)
endfunction