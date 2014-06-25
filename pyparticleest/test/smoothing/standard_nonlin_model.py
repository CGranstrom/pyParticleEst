import numpy
import math
import  pyparticleest.models.nlg as nlg
import pyparticleest.filter as pf
import matplotlib.pyplot as plt
import scipy.io


def generate_dataset(steps, P0, Q, R):
    x = numpy.zeros((steps+1,))
    y = numpy.zeros((steps+1,))
    x[0] = numpy.random.multivariate_normal((0.0,), P0)
    y[0] = 0.05*x[0]**2 + numpy.random.multivariate_normal((0.0,), R)
    for k in range(0,steps):
        x[k+1] = 0.5*x[k] + 25.0*x[k]/(1+x[k]**2) + 8*math.cos(1.2*k) + numpy.random.multivariate_normal((0.0,), Q)
        y[k+1] = 0.05*x[k+1]**2 + numpy.random.multivariate_normal((0.0,), R)
        
    return (x,y)

def wmean(logw, val):
    w = numpy.exp(logw)
    w = w / sum(w)
    return numpy.sum(w*val.ravel())

class Model(nlg.NonlinearGaussianInitialGaussian):
    """ x_{k+1} = 0.5*x_k + 25.0*x_k/(1+x_k**2) + 8*math.cos(1.2*k) + v_k, v_k ~ N(0,Q)
        y_k = 0.05*x_k**2 + e_k, e_k ~ N(0,R),
        x(0) ~ N(0,P0) """
    
    def __init__(self, P0, Q, R):
        super(Model, self).__init__(Px0=P0, Q=Q, R=R)
    
    def get_g(self, particles, t):
        return 0.05*particles**2
   
    def get_f(self, particles, u, t):
        return 0.5*particles + 25.0*particles/(1+particles**2) + 8*math.cos(1.2*t)
    
    
if __name__ == '__main__':
    
    
    data = scipy.io.loadmat("data/standard_nonlin_data1.mat")
    N = 100
    M = 5
    iterations = 1 #000
    x = data['x'].T
    y = data['y'].T
    
    x=x[:80]
    y=y[:80]
    
    T = len(y)
    P0 = 5.0*numpy.eye(1)
    Q = 1.0*numpy.eye(1)
    R = 0.1*numpy.eye(1)
    
    plt.ion()
     
#     plt.plot(range(T), 0.05*x**2, 'rx')
#     plt.plot(range(T), y, 'bx')
#     plt.plot(range(T), -numpy.sqrt(numpy.abs(y)/0.05), 'b--')
#     plt.plot(range(T), numpy.sqrt(numpy.abs(y)/0.05), 'b--')
    
    model = Model(P0, Q, R)
    rmse_filt = 0.0
    rmse_smooth = 0.0
    rmse2_filt = 0.0
    rmse2_smooth = 0.0
    for it in xrange(iterations):
        
        plt.clf()    
        plt.plot(range(T), x, 'r-', linewidth=2.0, label='True')
        traj = pf.ParticleTrajectory(model, N)
        traj.measure(y[0])
        for k in range(1,len(y)):
            traj.forward(u=None, y=y[k])
        
        est_filt = numpy.zeros((T,1))    
        for k in xrange(T):
            est_filt[k] = wmean(traj.traj[k].pa.w, traj.traj[k].pa.part)
        
        err = est_filt - x
        rmse_filt += numpy.sqrt(numpy.mean(err**2))
        
        tmp = 0.0
        wtmp = numpy.exp(traj.traj[0].pa.w)
        wnorm = wtmp / numpy.sum(wtmp)
        plt.plot((0,)*N, traj.traj[0].pa.part.ravel(), 'k.', markersize=0.5, label='Particles')
        for t in xrange(1,T):
            wtmp = numpy.exp(traj.traj[t].pa.w)
            wnorm = wtmp / numpy.sum(wtmp)
            plt.plot((t,)*N, traj.traj[t].pa.part.ravel(), 'k.', markersize=0.5)
            tmp += numpy.sum(wnorm*(traj.traj[t].pa.part[:,0]-x[t,0])**2)
        rmse2_filt += numpy.sqrt(tmp/T)
        
        if (M > 0):
            straj = traj.perform_smoothing(M, method='rsas', smoother_options={'R': 20})
            est_smooth = numpy.mean(straj.traj,1)
        
            err = est_smooth -x
            rmse_smooth += numpy.sqrt(numpy.mean(err**2))
        
            tmp = 0.0
            for k in xrange(M):
                tmp += 1.0/M*numpy.sum((straj.traj[:,k]-x)**2)
#                 plt.plot(range(T), straj.traj[:,k], 'k--')
            rmse2_smooth += numpy.sqrt(tmp/T)
        plt.ioff()
        plt.plot(range(T), est_filt, 'g--', linewidth=2.0, label='Filter mean')
        plt.plot(range(T), est_smooth, 'b--', linewidth=2.0, label='Smoother mean')
        plt.legend(loc=4, fontsize=24)
        plt.draw()
        plt.show()
    print "rmse filter = %f" % (rmse_filt / iterations)
    print "rmse smooth = %f" % (rmse_smooth / iterations)
    print "rmse2 filter = %f" % (rmse2_filt / iterations)
    print "rmse2 smooth = %f" % (rmse2_smooth / iterations)
    
    