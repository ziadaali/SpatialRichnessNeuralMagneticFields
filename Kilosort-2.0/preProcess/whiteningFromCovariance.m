function Wrot = whiteningFromCovariance(CC)
% takes as input the matrix CC of channel pairwise correlations
% outputs a symmetric rotation matrix (also Nchan by Nchan) that rotates
% the data onto uncorrelated, unit-norm axes

% ZIAD - Modified to double(CC) from CC
[E, D] 	= svd(double(CC)); % covariance eigendecomposition (same as svd for positive-definite matrix)
D       = diag(D); % take the non-zero values from the diagonal
eps 	= 1e-6;
Wrot 	= E * diag(1./(D + eps).^.5) * E'; % this is the symmetric whitening matrix (ZCA transform)

save('ziad_cov', 'E', 'D', 'Wrot', 'CC');
