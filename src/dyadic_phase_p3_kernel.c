/* Exact P3 two-level finite-instrument replay. No RNG and no oracle inputs. */
#include <math.h>
#include <stddef.h>

static void half_rotate(double *x, double *y, double *p,
                        double nx, double ny, double ca, double sa) {
    double rx=2*(*x), ry=-2*(*y), rz=1-2*(*p);
    double dot=nx*rx+ny*ry;
    double xx=ca*rx+sa*ny*rz+(1-ca)*nx*dot;
    double yy=ca*ry-sa*nx*rz+(1-ca)*ny*dot;
    double zz=ca*rz+sa*(nx*ry-ny*rx);
    *x=xx/2; *y=-yy/2; *p=(1-zz)/2;
}

int p3_local_filter(size_t count, size_t steps, size_t burn,
                    double g, double gamma, double eta, double dt,
                    const double *phases, const double *records, double *out) {
    double pd=-expm1(-gamma*dt), survival=exp(-gamma*dt/2);
    double ca=cos(g*dt), sa=sin(g*dt), factor=sqrt(eta*pd/dt);
    for(size_t q=0;q<count;q++) {
        double x=0,y=0,p=0,loglaw=0,nx=cos(phases[q]),ny=sin(phases[q]);
        for(size_t block=0;block<2;block++) {
            for(size_t k=0;k<burn+steps;k++) {
                half_rotate(&x,&y,&p,nx,ny,ca,sa);
                if(k<burn) { x*=survival; y*=survival; p*=survival*survival; }
                else {
                    double dy=records[block*steps+k-burn];
                    double u=block==0?factor*dy:0, v=block==0?0:-factor*dy;
                    double norm=1+2*(u*x+v*y)+eta*pd*(dy*dy/dt-1)*p;
                    if(!(norm>0) || !isfinite(norm)) return 1;
                    x=survival*(x+u*p)/norm;
                    y=survival*(y+v*p)/norm;
                    p=survival*survival*p/norm;
                    loglaw+=log(norm);
                }
                half_rotate(&x,&y,&p,nx,ny,ca,sa);
            }
        }
        out[q]=loglaw;
    }
    return 0;
}

/* Full arithmetic ket engine. Inefficient output is represented by an explicit
 * unobserved Kraus branch. Discarding that branch gives the frozen mixed-state
 * homodyne instrument exactly. Its label is NOT operational inference input.
 * NumPy supplies the sealed PCG64 uniform stream through a callback. */
#include <complex.h>
#include <stdint.h>

typedef double (*uniform_fn)(void *);
typedef struct { uniform_fn next; void *state; int spare_valid; double spare; } stream;
static double normal_draw(stream *r) {
    if(r->spare_valid) {r->spare_valid=0;return r->spare;}
    double u; do {u=r->next(r->state);} while(u<=0);
    double radius=sqrt(-2*log(u)), angle=6.2831853071795864769*r->next(r->state);
    r->spare=radius*sin(angle);r->spare_valid=1;return radius*cos(angle);
}
static void ket_half(double complex *v,int D,const int64_t *permutation,double c,double s) {
    double complex temp[64];
    for(int k=0;k<D;k++) temp[k]=c*v[k]-I*s*v[permutation[k]];
    for(int k=0;k<D;k++) v[k]=temp[k];
}
static double norm2(double complex z) {return creal(z)*creal(z)+cimag(z)*cimag(z);}

/* Deterministic Kraus branch; used by prechecks with explicitly chosen y/branch. */
int p3_ket_branch(int D,int mask,double pd,double eta,double angle,double y,int hidden,
                  const double complex *input,double complex *output,double *weight) {
    if(D<2 || D>64 || mask<1 || mask>=D || eta<0 || eta>1 || pd<0 || pd>=1) return 1;
    double complex b=sqrt(eta*pd)*cexp(-I*angle)*y;
    double survival=sqrt(1-pd),total=0;
    for(int k=0;k<D;k++) if(!(k&mask)) {
        int e=k|mask;
        output[k]=hidden?sqrt((1-eta)*pd)*input[e]:input[k]+b*input[e];
        output[e]=hidden?0:survival*input[e];
        total+=norm2(output[k])+norm2(output[e]);
    }
    *weight=total;
    return 0;
}
static int observed_ket(double complex *v,int D,int mask,double pd,double eta,double angle,
                         stream *r,double *dy,double dt,uint64_t *hidden_count) {
    double pe=0; double complex q=0;
    for(int k=0;k<D;k++) if(!(k&mask)) {pe+=norm2(v[k|mask]);q+=v[k|mask]*conj(v[k]);}
    double a=1-eta*pd*pe,c=eta*pd*pe,b=2*sqrt(eta*pd)*creal(cexp(-I*angle)*q);
    double y=0;int accepted=0;
    for(int attempt=0;attempt<128;attempt++) {
        if(r->next(r->state)<.5) y=normal_draw(r);
        else {double n0=normal_draw(r),n1=normal_draw(r),n2=normal_draw(r);
              y=sqrt(n0*n0+n1*n1+n2*n2)*(r->next(r->state)<.5?-1:1);}
        double chance=(a+b*y+c*y*y)/(1+y*y);
        if(chance < -1e-10 || chance > 1+1e-10) return 2;
        if(r->next(r->state)<chance) {accepted=1;break;}
    }
    if(!accepted) return 3;
    double norm=a+b*y+c*y*y,hidden=(1-eta)*pd*pe;
    int branch=r->next(r->state)*norm<hidden;
    double complex out[64];double weight;
    if(p3_ket_branch(D,mask,pd,eta,angle,y,branch,v,out,&weight) || !(weight>0))return 4;
    for(int k=0;k<D;k++)v[k]=out[k]/sqrt(weight);
    *hidden_count+=branch;*dy=sqrt(dt)*y;
    return 0;
}

/* profile=0 DP-P,1 DP-S,2 fresh-data negative control.
 * DP-S/fresh compiled operators act on a single probe plus the full data.
 * Reference reset is explicit; data reset occurs ONLY for profile=2. */
int p3_generate(int profile,int m,int d,int steps,int burn,double g,double gamma,
                double eta,double dt,const double *chi,const int64_t *permutations,
                const double complex *initial,void *rng_state,uniform_fn next,
                double *signal,double *reference,double complex *final,
                uint64_t *counters) {
    int D=profile==0?d*(1<<m):2*d;
    if(profile<0 || profile>2 || m<1 || m>3 || D>64 || steps<1 || burn<0)return 1;
    double complex state[64],refs[3][2];
    for(int k=0;k<D;k++)state[k]=initial[k];
    for(int j=0;j<m;j++){refs[j][0]=1;refs[j][1]=0;}
    int64_t refperm[2]={1,0};
    stream r={next,rng_state,0,0};
    double pd=-expm1(-gamma*dt),c=cos(g*dt/2),s=sin(g*dt/2);
    for(int k=0;k<8;k++)counters[k]=0;
    counters[0]=1; /* data preparation count */
    if(profile==0) {
        for(int block=0;block<2;block++)for(int t=0;t<burn+steps;t++)for(int j=0;j<m;j++) {
            double command=block*1.5707963267948966192,dy;
            ket_half(state,D,permutations+j*D,c,s);
            int status=observed_ket(state,D,d*(1<<(m-j-1)),pd,eta,command-chi[j],&r,&dy,dt,&counters[1]);
            if(status)return 10+status;
            ket_half(state,D,permutations+j*D,c,s);
            if(t>=burn)signal[(j*2+block)*steps+t-burn]=dy;
            ket_half(refs[j],2,refperm,c,s);
            status=observed_ket(refs[j],2,1,pd,eta,command-chi[j],&r,&dy,dt,&counters[2]);
            if(status)return 20+status;
            ket_half(refs[j],2,refperm,c,s);
            if(t>=burn)reference[(j*2+block)*steps+t-burn]=dy;
            counters[3]+=2; /* arithmetic half-unitary applications */
        }
    } else {
        for(int j=0;j<m;j++) {
            refs[0][0]=1;refs[0][1]=0; /* complete unobserved reference reset */
            if(j>0) {
                double pe=0;for(int k=d;k<D;k++)pe+=norm2(state[k]);
                int branch=r.next(r.state)<pe;double weight=branch?pe:1-pe;
                if(!(weight>0))return 30;
                for(int k=0;k<d;k++)state[k]=state[k+branch*d]/sqrt(weight);
                for(int k=d;k<D;k++)state[k]=0;
                counters[4]++;counters[5]+=branch; /* unobserved reset environment */
                if(profile==2){for(int k=0;k<D;k++)state[k]=0;state[1]=1;counters[0]++;}
            }
            for(int block=0;block<2;block++)for(int t=0;t<burn+steps;t++) {
                double command=block*1.5707963267948966192,dy;
                ket_half(state,D,permutations+j*D,c,s);
                int status=observed_ket(state,D,d,pd,eta,command-chi[j],&r,&dy,dt,&counters[1]);
                if(status)return 40+status;
                ket_half(state,D,permutations+j*D,c,s);
                if(t>=burn)signal[(j*2+block)*steps+t-burn]=dy;
                ket_half(refs[0],2,refperm,c,s);
                status=observed_ket(refs[0],2,1,pd,eta,command-chi[j],&r,&dy,dt,&counters[2]);
                if(status)return 50+status;
                ket_half(refs[0],2,refperm,c,s);
                if(t>=burn)reference[(j*2+block)*steps+t-burn]=dy;
                counters[3]+=2;
            }
        }
    }
    for(int k=0;k<D;k++)final[k]=state[k];
    return 0;
}
