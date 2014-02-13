'''
Created on Sep 17, 2013

@author: ajn
'''
import pyparticleest.param_est as param_est
import numpy
import matplotlib.pyplot as plt

import pyparticleest.test.mixed_nlg.initial.particle_param_init as particle_param_init
from pyparticleest.test.mixed_nlg.initial.particle_param_init import ParticleParamInit as PartModel

class GradPlot():
    def __init__(self, params, vals, diff):
        self.params = params
        self.vals = vals
        self.diff = diff

    def plot(self, fig_id):
        fig = plt.figure(fig_id)
        fig.clf()
        plt.plot(self.params, self.vals)
        for k in range(len(self.params)):
            if (k % 10 == 1):
                self.draw_gradient(self.params[k], self.vals[k], self.params[k]-self.params[k-1], self.diff[:,k])
                
        plt.show()
        
    def draw_gradient(self, x, y, dx, dydx):
        plt.plot((x-dx, x+dx), (y-dydx*dx, y+dydx*dx), 'r')
        


P0 = 100.0*numpy.eye(1)
Qz = numpy.diag([0.1])
R = numpy.diag([0.01])
    
class GradientTest(param_est.ParamEstimation):

    def create_initial_estimate(self, params, num):
        self.params = params
        particles = numpy.empty(num, PartModel)
        for k in range(len(particles)):
            particles[k] = PartModel(P0=P0, Qz=Qz, R=R, params=params)
        return particles
    
    def test(self, param_id, param_vals, num=100, nums=1):
        self.simulate(num_part=num, num_traj=nums)
        param_steps = len(param_vals)
        logpy = numpy.zeros((param_steps,))
        grad_lpy = numpy.zeros((len(self.params), param_steps))
        logpxn = numpy.zeros((param_steps,))
        grad_lpxn = numpy.zeros((len(self.params), param_steps))
        logpx0 = numpy.zeros((param_steps,))
        grad_lpx0 = numpy.zeros((len(self.params), param_steps))
        for k in range(param_steps):    
            tmp = numpy.copy(self.params)
            tmp[param_id] = param_vals[k]
            
            self.set_params(tmp.ravel())
            logpy[k] = self.eval_logp_y()
            logpxn[k] = self.eval_logp_xnext()
            logpx0[k] = self.eval_logp_x0()
            grad_lpy[:,k] = self.eval_grad_logp_y()
            grad_lpxn[:,k] = self.eval_grad_logp_xnext()
            grad_lpx0[:,k] = self.eval_grad_logp_x0()

        self.plot_y = GradPlot(param_vals, logpy, grad_lpy)
        self.plot_xn = GradPlot(param_vals, logpxn, grad_lpxn)
        self.plot_x0 = GradPlot(param_vals, logpx0, grad_lpx0)

    def plot_estimate(self, states, y):
        svals = numpy.zeros((1, nums, steps+1))
        for i in range(steps+1):
            for j in range(len(self.straj)):
                svals[:,j,i]=self.straj[j].traj[i].kf.z.ravel()
                
        plt.figure()
        y = numpy.asarray(y)
        y = y.ravel()
        for j in range(nums):
            plt.plot(range(steps+1),svals[0,j,:],'g-')
            plt.plot(range(steps+1),states[0,:],'go')
            plt.plot(range(1,steps+1),y,'bx')
            
        plt.show()
        plt.draw()
    
if __name__ == '__main__':
    
    num = 1
    nums=1
    sims = 1
    
    z0_true = numpy.array((2.0,))
    
    # How many steps forward in time should our simulation run
    steps = 32
    
    # Create reference
    (ylist, states) = particle_param_init.generate_reference(P0=P0, Qz=Qz, R=R, params=z0_true, steps=steps)

    # Create an array for our particles 
    gt = GradientTest(u=None, y=ylist)
    gt.set_params(numpy.array((z0_true,)).reshape((-1,1)))
    
    param_steps = 101
    param_vals = numpy.linspace(-10.0, 10.0, param_steps)
    gt.test(0, param_vals)

    gt.plot_estimate(states, ylist)
    gt.plot_y.plot(1)
    gt.plot_xn.plot(2)
    gt.plot_x0.plot(3)
    
    