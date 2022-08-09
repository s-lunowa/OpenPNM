import numpy as np
from openpnm.utils import Docorator


docstr = Docorator()


__all__ = [
    "water_correlation",
    "liquid_pure_bb",
    "liquid_mixture_wsd",
]


@docstr.dedent
def water_correlation(phase, T='pore.temperature', salinity='pore.salinity'):
    r"""
    Calculates surface tension of pure water or seawater at atmospheric
    pressure using Eq. (28) given by Sharqawy et al. Values at
    temperature higher than the normal boiling temperature are calculated at
    the saturation pressure.

    Parameters
    ----------
    %(models.target.parameters)s
    %(models.phase.T)s
    salinity : str
        The dictionary key containing the salinity values. Salinity must be
        expressed in g of salt per kg of solution (ppt).

    Returns
    -------
    value : ndarray
        A numpy ndarray containing surface tension of seawater in [N/m]

    Notes
    -----
    T must be in K, and S in g of salt per kg of phase, or ppt (parts per
    thousand). The correlation is valid for 273 < T < 313 K and
    0 < S < 40 g/kg within 0.2% accuracy.

    References
    ----------
    Sharqawy M. H., Lienhard J. H., and Zubair, S. M., Desalination and
    Water Treatment, 2010.

    """
    T = phase[T]
    if salinity in phase.keys():
        S = phase[salinity]
    else:
        S = 0
    sigma_w = 0.2358*((1-(T/647.096))**1.256)*(1-0.625*(1-(T/647.096)))
    a1 = 2.2637334337E-04
    a2 = 9.4579521377E-03
    a3 = 3.3104954843E-02
    TC = T-273.15
    sigma_sw = sigma_w*(1+(a1*TC+a2)*np.log(1+a3*S))
    value = sigma_sw
    return value


@docstr.dedent
def liquid_pure_bb(
    phase,
    T='pore.temperature',
    Tc='param.critical_temperature',
    Tb='param.boiling_temperature',
    Pc='param.critical_pressure',
):
    r"""
    Uses Brock_Bird model

    Parameters
    ----------
    %(models.target.parameters)s
    %(models.phase.T)s
    critical_temperature : str
        The dictionary key containing the critical temperature values (K)

    Returns
    -------
    value : ndarray
        A numpy ndarray containing surface tension values scaled to the
        temperature [N/m]

    """
    # brock_bird
    T = phase[T]
    Tc = phase[Tc]
    Tr = T/Tc
    Tb = phase[Tb]
    Tbr = Tb/Tc
    Pc = phase[Pc]/100000
    Q = 0.1196*(1 + Tbr*np.log(Pc/1.01325)/(1-Tbr))-0.279
    sigma = 1e-3 * Q * (Pc**(2/3)) * (Tc**(1/3)) * ((1-Tr)**(11/9))
    return sigma


def liquid_mixture_wsd(
    phase,
    sigmas='pore.surface_tension.*',
    rhos='pore.density.*',
    MWs='param.molecular_weight.*',
):
    r"""
    """
    # winterfelf_scriven_davis
    sigmas = phase.get_comp_vals(sigmas)
    xs = phase['pore.mole_fraction']
    rhos = phase.get_comp_vals(rhos)  # kg/m3
    MWs = phase.get_comp_vals(MWs)  # g/mol
    rhoms = {k: rhos[k]/(MWs[k]/1000) for k in xs.keys()}  # mol/m3
    rhom_mix = np.vstack([rhoms[k]*xs[k] for k in xs.keys()]).sum(axis=0)
    sigma = 0.0
    for i, ki in enumerate(xs.keys()):
        for j, kj in enumerate(xs.keys()):
            num = xs[ki]*xs[kj]*(rhom_mix**2)*(sigmas[ki]*sigmas[kj])**0.5
            denom = rhoms[ki]*rhoms[kj]
            sigma += num/denom
    return sigma
