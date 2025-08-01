function [err] = mismatch(mat1,mat2)

err = max(abs(mat1-mat2), [], 'all');

end