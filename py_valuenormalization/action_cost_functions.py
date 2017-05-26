from math import pow
###########################################################################################################
################### P A R A M E T E R S ###################################################################
###########################################################################################################
curr_user = None 
alpha = 0.7
rho_f_const = 500
rho_s_const = 500

default_show_opt = False

###########################################################################################################
################### C O S T   F U N C T I O N S ###########################################################
###########################################################################################################
def calc_purity(c, G):
    H = {}

    if len(c) == 0:
        return None

    for v in c:
        if G[v] not in H:
            H[G[v]] = []
        H[G[v]].append(v)
    SH = sorted([lbl for lbl in H], key = lambda x : len(H[x]), reverse = True)
    return (len(H[SH[0]])*1./len(c), len(H[SH[0]]), len(c))


def rho_f(x, user=curr_user, show=default_show_opt):
    cost = rho_f_const
    if show: print("[[[ USER OP ]]] focus(%s)\t[cost = %d]"%(str(x), cost))
    return cost


def rho_s(x, user=curr_user, show=default_show_opt):
    cost = rho_s_const
    if show: print("[[[ USER OP ]]] select(%s)\t[cost = %d]"%(str(x), cost))
    return cost


def rho_m(x, y, user=curr_user, show=default_show_opt):
    cost = user['rho_m']
    if show: print("[[[ USER OP ]]] match(%s, %s)\t[cost = %d]"%(str(x), str(y), cost))
    return cost


def rho_p(x, G=None, inpalpha=None, user=curr_user, show=default_show_opt, clust_size=None):
    curalpha = alpha
    if inpalpha is not None:
        curalpha = inpalpha
    elif G is not None:
        (curalpha,_,_) = calc_purity(x, G)
    psi = len(x)
    if clust_size is not None:
        psi = clust_size
    cost = user['gamma'] * curalpha * psi + user['gamma_0']
    if show: print("[[[ USER OP ]]] isPure(%s)\t[cost = %.02f]"%(str(x), cost))
    return cost


def rho_d(x, stm_capacity, user=curr_user, show=default_show_opt, clust_size=None):
    psi = len(x)
    if clust_size is not None:
        psi = clust_size
    cost = user['eta_1'] * psi
    if psi > stm_capacity:
        cost = user['eta_2'] * pow(psi, 2)
    if show: print("[[[ USER OP ]]] findDomEntityValue(%s)\t[cost = %.02f]"%(str(x), cost))
    return cost


def rho_r(x, user=curr_user, show=default_show_opt):
    cost = user['rho_r']
    if show: print("[[[ USER OP ]]] recall(%s)\t[cost = %%.02f]"%(str(x), cost))
    return cost


def rho_z(x, user=curr_user, show=default_show_opt):
    cost = user['rho_z']
    if show: print("[[[ USER OP ]]] recallAndMemorize(%s)\t[cost = %%.02f]"%(str(x), cost))
    return cost


