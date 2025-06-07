#version 330

uniform vec2 pos;
uniform float strength;

in vec2 texCoord;
out vec4 fragColor;

const vec3 suncolor=vec3(.643,.494,.867);

#define CHEAP_FLARE//faster but cheap looking

float getSun(vec2 uv){
	return length(uv)<.009?1.:0.;
}

//from: https://www.shadertoy.com/view/XdfXRX
vec3 lensflares(vec2 uv,vec2 pos,out vec3 sunflare,out vec3 lensflare)
{
	vec2 main=uv-pos;
	vec2 uvd=uv*(length(uv));
	
	float ang=atan(main.y,main.x);
	float dist=length(main);
	dist=pow(dist,.1);
	
	float f0=1./(length(uv-pos)*25.+1.);
	f0=pow(f0,2.);
	
	f0=f0+f0*(sin((ang+1./18.)*12.)*.1+dist*.1+.8);
	
	float f2=max(1./(1.+32.*pow(length(uvd+.8*pos),2.)),.0)*.25;
	float f22=max(1./(1.+32.*pow(length(uvd+.85*pos),2.)),.0)*.23;
	float f23=max(1./(1.+32.*pow(length(uvd+.9*pos),2.)),.0)*.21;
	
	vec2 uvx=mix(uv,uvd,-.5);
	
	float f4=max(.01-pow(length(uvx+.4*pos),2.4),.0)*6.;
	float f42=max(.01-pow(length(uvx+.45*pos),2.4),.0)*5.;
	float f43=max(.01-pow(length(uvx+.5*pos),2.4),.0)*3.;
	
	uvx=mix(uv,uvd,-.4);
	
	float f5=max(.01-pow(length(uvx+.2*pos),5.5),.0)*2.;
	float f52=max(.01-pow(length(uvx+.4*pos),5.5),.0)*2.;
	float f53=max(.01-pow(length(uvx+.6*pos),5.5),.0)*2.;
	
	uvx=mix(uv,uvd,-.5);
	
	float f6=max(.01-pow(length(uvx-.3*pos),1.6),.0)*6.;
	float f62=max(.01-pow(length(uvx-.325*pos),1.6),.0)*3.;
	float f63=max(.01-pow(length(uvx-.35*pos),1.6),.0)*5.;
	
	sunflare=vec3(f0);
	lensflare=vec3(f2+f4+f5+f6,f22+f42+f52+f62,f23+f43+f53+f63);
	
	return sunflare+lensflare;
}
//

vec3 anflares(vec2 uv,float threshold,float intensity,float stretch,float brightness)
{
	threshold=1.-threshold;
	
	vec3 hdr=vec3(getSun(uv));
	hdr=vec3(floor(threshold+pow(hdr.r,1.)));
	
	float d=intensity;
	float c=intensity*stretch;
	
	for(float i=c;i>-1.;i--){
		float texL=getSun(uv+vec2(i/d,0.));
		float texR=getSun(uv-vec2(i/d,0.));
		
		hdr+=floor(threshold+pow(max(texL,texR),4.))*(1.-i/c);
	}
	
	return hdr*brightness;
}

vec3 anflares(vec2 uv,float intensity,float stretch,float brightness)
{
	uv.x*=1./(intensity*stretch);
	uv.y*=.5;
	return vec3(smoothstep(.009,0.,length(uv)))*brightness;
}

void main(){
	// Normalized pixel coordinates (from 0 to 1)
	vec2 uv=texCoord;
	vec2 mouse=(pos.xy+1.)*.5;
	vec3 col;
	vec3 sun,sunflare,lensflare;
	vec3 flare=lensflares(uv*1.5,mouse*1.5,sunflare,lensflare);
	
	#ifdef CHEAP_FLARE
	vec3 anflare=pow(anflares(uv-mouse,400.,.5,.6),vec3(4.));
	anflare+=smoothstep(.0025,1.,anflare)*10.;
	anflare*=smoothstep(0.,1.,anflare);
	#else
	vec3 anflare=pow(anflares(uv-mouse,.5,400.,.9,.1),vec3(4.));
	#endif
	
	sun+=getSun(uv-mouse)+(flare+anflare)*suncolor*2.;
	col+=sun;
	
	//col = 1.0 - exp(-1.0 * col);
	col=pow(col,vec3(1./2.2));
	
	// Output to screen
	fragColor=vec4(col,1.)*strength;
}